import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection_pool
from data_manager.emd.emd import get_emd_by_geo_codes
from data_manager.emd.geo import get_emd_geo
from data_manager.emd.communes_with_emd import are_communes_covered_by_emd
from data_manager.entd.entd import get_entd_persons, get_entd_travels
from data_manager.exception import UnknownGeocodeError
from data_manager.insee_mobpro.flows_home_work import WORK_FLOWS_THRESHOLD
from data_manager.osm.railways import get_railways
from data_manager.transportdatagouv.zfe import get_zfe
from model.commune import InfluenceCommune, ResidentialCommune, WorkCommune
from model.public_transport import PublicTransport

from model.functions.commuter_matrix import build_commuter_matrix, build_commuter_matrix_per_mode
from model.functions.commuter_transport_matrix import create_set_work_area_function
from model.functions.compute_matching_indicators import compute_matching_indicators
from model.functions.standardisation import compute_indicators, compute_attributes, compute_zones
from model.place import Place
from model.territorial_anchorage.distances_matrix import get_distances_matrix_areas, get_distances_matrix
from model.territorial_anchorage.set_main_activities import set_main_activities
from model.territorial_anchorage.set_residential_area import set_residential_area
from model.synthetic_population.synthetic_population import get_synthetic_population
from model.mobility_pattern.population_association import match_synthetic_population_with_entd_sources
from model.mobility_pattern.location_assignment import match_work_location, match_education_location, \
    set_residential_location, match_secondary_location, match_other_location
from data_manager.main import get_public_transport, get_sources

pool = mariadb_connection_pool()


class Territory:
    """
    Territory is the main class to build the model and to study the travels.
    """

    def __init__(self, name, communes_geo_codes, zones, influence_communes_geo_codes):
        """
        Constructor
        """
        self.name = name
        self.communes_geo_codes = communes_geo_codes
        self.influence_communes_geo_codes = influence_communes_geo_codes
        self.work_communes_geo_codes = []
        print("--- residential communes")
        self.communes = [ResidentialCommune(pool, geo_code, zone) for geo_code, zone in zip(communes_geo_codes, zones)]
        print("--- influence communes")
        self.influence_communes = [InfluenceCommune(pool, geo_code) for geo_code in influence_communes_geo_codes]
        print("--- work communes")
        self.work_communes = self.create_work_communes()

        self.all_areas = self.get_all_areas()
        self.all_places = self.get_all_places()

        print("--- public transport")
        self.public_transport = [PublicTransport(pt["route_id"],
                                                 pt["route_short_name"],
                                                 pt["route_long_name"],
                                                 pt["route_type"],
                                                 pt["stops_name"],
                                                 pt["stops_lat"],
                                                 pt["stops_lon"]) for pt in get_public_transport(pool, communes_geo_codes)]
        print(f"Found {len(self.public_transport)} public transport routes")
        self.railways = sum(
            [get_railways(pool, geo_code) for geo_code in communes_geo_codes + influence_communes_geo_codes], [])
        self.pt_stops = self.get_pt_stops()

        self.zfe = get_zfe(pool, communes_geo_codes + influence_communes_geo_codes + self.work_communes_geo_codes)

        # PREREQUISITE TO BUILD TRAVEL DEMAND
        self.mobility_survey_persons = get_entd_persons(pool)
        self.mobility_survey_travels = get_entd_travels(pool)

        self.sources = get_sources()

        # BUILDING SYN POP & TRAVELS DEMAND
        self.synthetic_population, self.travels_demand = self.build_pop_and_travels()

    def create_work_communes(self):
        work_communes = []
        work_communes_geo_codes = []

        def update_work_communes(geo_code, c):
            work_communes.append(WorkCommune(pool, geo_code))
            work_communes_geo_codes.append(geo_code)
            self.work_communes_geo_codes.append(geo_code)

        [[update_work_communes(geo_code, c)
          for geo_code, name, lat, lon, flow in c.flows_home_work
          if geo_code not in self.communes_geo_codes + self.influence_communes_geo_codes + work_communes_geo_codes
          and flow >= WORK_FLOWS_THRESHOLD]
         for c in self.communes]

        return work_communes

    def get_all_areas(self):
        all_communes = self.communes + self.influence_communes + self.work_communes
        all_areas = sum([c.residential_areas + c.work_areas + c.cluster_areas for c in all_communes], [])
        return all_areas

    def get_all_places(self):
        all_communes = self.communes + self.influence_communes + self.work_communes
        all_places = sum([c.places for c in all_communes], [])
        return all_places

    def get_area_by_id(self, id):
        all_areas = self.all_areas
        area = [a for a in all_areas if a.id == id]
        return area[0] if len(area) > 0 else None

    def get_commune_by_geo_code(self, geo_code):
        all_communes = self.communes + self.influence_communes + self.work_communes
        commune = [c for c in all_communes if c.geo_code == geo_code]
        return commune[0] if len(commune) > 0 else None

    def get_commune_by_area_id(self, id):
        all_communes = self.communes + self.influence_communes + self.work_communes
        area = sum(
            [[c for a in c.residential_areas + c.work_areas + c.cluster_areas if a.id == id] for c in all_communes], [])
        return area[0] if len(area) > 0 else None

    def get_pt_stops(self):
        pt_stops = sum([[Place(name, 1, [lat, lon], "stop", "arrêt de transport en commun",
                               "public transport", "transport en commun", "other", "autre")
                         for name, lat, lon in zip(pt.stops_name, pt.stops_lat, pt.stops_lon)]
                        for pt in self.public_transport], [])
        train_stops = [p for p in self.all_places if p.type == "railway station"]
        return pt_stops + train_stops

    def build_synthetic_population(self):
        # 1 - raw synthetic population from census
        synthetic_population = get_synthetic_population(pool, self.communes_geo_codes)

        synthetic_population_5 = synthetic_population[synthetic_population["age"] > 5]

        # 2 - set a residential area to each household
        syn_pop_with_ra_places = set_residential_area(self.communes,
                                                      synthetic_population_5)
        # 3 - compute matching indicators
        dist_ra_stops_matrix = get_distances_matrix(sum([c.residential_areas for c in self.communes], []),
                                                    self.pt_stops)
        syn_pop_with_indicators = compute_matching_indicators(syn_pop_with_ra_places, dist_ra_stops_matrix)
        # 4 - assign places of characteristic activities: work, education, food shops
        syn_pop_with_activities_places = set_main_activities(syn_pop_with_indicators,
                                                             self.all_areas,
                                                             self.areas_distances_matrix,
                                                             self.commuter_matrix,
                                                             self.commuter_distances_matrix,
                                                             self.set_work_area)
        print("--- synthetic population")
        print(syn_pop_with_activities_places)
        return syn_pop_with_activities_places

    def build_travels_demand(self, pool, syn_pop):
        # 1 - first some correction on emp coefs
        travels_entd = pd.merge(self.mobility_survey_travels,
                                self.mobility_survey_persons[["id_ind", "w_ind"]],
                                on="id_ind", how="left")
        travels_entd["w_trav"] = travels_entd["w_trav"] / travels_entd["w_ind"]
        travels_entd = travels_entd.drop(columns=["w_ind"])
        self.mobility_survey_travels = travels_entd

        # 2 - associate activity chains from EMP
        syn_pop_with_activity = match_synthetic_population_with_entd_sources(syn_pop, self.mobility_survey_persons,
                                                                             travels_entd)
        # 3 - assign associated travels to synthetic population
        all_travels = pd.merge(syn_pop_with_activity, self.mobility_survey_travels,
                               left_on="source_id", right_on="id_ind")

        # now, we have to find origin & destination to each travel
        # 4 - associate primary locations
        all_travels = set_residential_location(all_travels)
        all_travels = match_work_location(all_travels)
        all_travels = match_education_location(all_travels, self.all_areas, self.areas_distances_matrix)
        all_travels = match_other_location(all_travels, self.all_areas, self.areas_distances_matrix)

        # 5 - associate secondary locations
        all_travels = match_secondary_location(all_travels, self.all_areas, self.areas_distances_matrix)

        # 6 - cleaning & standardisation of data
        all_travels = compute_indicators(all_travels, self.areas_distances_matrix)
        all_travels = compute_attributes(all_travels, self)

        print("--- travels demand")
        print(all_travels, end='\n\n')
        return syn_pop_with_activity, all_travels

    def build_pop_and_travels(self):
        # here we check if a mobility local survey is available
        if are_communes_covered_by_emd(pool, self.communes_geo_codes):  # if this is the case, we use it
            syn_pop, travels, emd_id, emd_name = get_emd_by_geo_codes(pool, self.communes_geo_codes)
            print("--- survey population")
            print(syn_pop)
            syn_pop["id"] = syn_pop["id_ind"]
            travels = pd.merge(travels, syn_pop, on="id_ind")
            self.geo_zones = get_emd_geo(pool, emd_id)
            self.sources["emd"] = {"label": emd_name, "link": ""}

        else:  # if not, we estimate through the modelisation
            self.commuter_matrix, self.commuter_distances_matrix = build_commuter_matrix(self.communes,
                                                                                         self.influence_communes,
                                                                                         self.work_communes)
            self.commuter_matrix_per_mode, self.commuter_distances_matrix_per_mode = build_commuter_matrix_per_mode(
                self.communes,
                self.influence_communes,
                self.work_communes,
                self.commuter_matrix,
                self.commuter_distances_matrix)

            self.set_work_area = create_set_work_area_function(self.communes, self.influence_communes,
                                                               self.work_communes)
            self.areas_distances_matrix = get_distances_matrix_areas(self.all_areas)

            syn_pop = self.build_synthetic_population()
            syn_pop, travels = self.build_travels_demand(pool, syn_pop)
            syn_pop["w_ind"] = 1
            travels["w_ind"] = 1
            travels["w_trav"] = travels["w_trav"] / travels["w_ind"]

        travels = compute_zones(travels, self)
        return syn_pop, travels


if __name__ == "__main__":
    try:
        pd.set_option('display.max_columns', 50)
        pd.set_option('display.max_rows', 50)
        pd.set_option('display.width', 4000)

        test = Territory("test", ["79048"], [1], [])

    except UnknownGeocodeError as e:
        print(e.message)
