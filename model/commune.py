import pprint
import pandas as pd
from data_manager.exception import UnknownGeocodeError
from data_manager.geodip.precariousness import get_precariousness_prop
from data_manager.insee_general.aav import get_aav
from data_manager.insee_general.code_geo_postal import geo_code_to_postal_code, geo_code_to_name
from data_manager.insee_general.districts import city_to_districts
from data_manager.insee_general.epci import get_epci
from data_manager.insee_local.pop_age import get_pop_age_nb

from data_manager.insee_local.population import get_population
from data_manager.insee_filosofi.gridded_population import get_gridded_population
from data_manager.insee_local.pop_status_nb import get_pop_status_nb
from data_manager.insee_local.jobs_nb import get_jobs_nb
from data_manager.ign.commune_center import get_coords
from data_manager.insee_mobpro.flows_home_work import get_flows_home_work, get_flows_home_work_workers, \
    get_flows_home_work_trans
from data_manager.insee_local.workers_within_commune_prop import get_workers_within_commune_prop
from data_manager.insee_local.households_cars_nb import get_households_cars_nb
from data_manager.insee_filosofi.decile_ratio import get_decile_ratio
from data_manager.insee_filosofi.gini import get_gini
from data_manager.insee_filosofi.incomes import get_median_income
from data_manager.insee_local.topography import get_surface, get_artificialization_rate
from data_manager.insee_local.csp import get_csp

from model.functions.cluster import create_residential_areas_from_gridded_pop
from data_manager.main import get_places
from data_manager.ign.commune_outline import get_commune_outline
from data_manager.rsvero.critair import get_critair
from data_manager.transportdatagouv.bnlc import get_bnlc
from data_manager.transportdatagouv.cycle_parkings import get_cycle_parkings
from data_manager.transportdatagouv.cycle_paths import get_cycle_paths
from data_manager.transportdatagouv.irve import get_irve

from model.area import ResidentialArea, WorkArea, ClusterArea
from model.place import Place
from model.functions.cluster import cluster_single, split_clustered_data

CLUSTERING_DISTANCE = 1 #km
CLUSTERING_DISTANCE_INFLUENCE = 2 #km


class Commune:
    """
    Commune is the class which represent a commune.
    """

    def __init__(self, pool, geo_code, clustering_distance=CLUSTERING_DISTANCE):
        """
        Constructor.
        :param geo_code: (String) INSEE geo code of the concerned commune
        """
        self.geo_code = str(geo_code)
        self.name = geo_code_to_name(pool, geo_code)
        self.postal_code = geo_code_to_postal_code(pool, geo_code)
        self.coords = get_coords(pool, geo_code)

        self.districts = city_to_districts(pool, geo_code)

        self.population = get_population(pool, geo_code)
        self.status = get_pop_status_nb(pool, geo_code)

        self.jobs_nb = get_jobs_nb(pool, geo_code)
        self.workers_within_commune_prop = get_workers_within_commune_prop(pool, geo_code)
        self.flows_home_work = get_flows_home_work(pool, geo_code) # habitants
        self.flows_home_work_workers = get_flows_home_work_workers(pool, self.districts) # workers

        self.residential_areas = []
        self.work_areas = []
        self.places = []

        self.cycle_paths = get_cycle_paths(pool, self.districts)
        self.cycle_parkings = get_cycle_parkings(pool, geo_code)
        self.irve = get_irve(pool, self.districts + [geo_code])
        self.bnlc = get_bnlc(pool, geo_code)

        self.cycle_paths_length = round(self.cycle_paths["length_path"].sum())
        self.cycle_paths_length_per_hab = round(self.cycle_paths["length_path"].sum()/self.population, 2)

        self.clustering_distance = clustering_distance
        self.cluster_areas = [] #self.create_cluster_areas()

        self.households = []

    def to_dict_distance_matrix(self):
        return {
            "geo_code": self.geo_code,
            "coords": self.coords
        }

    def create_residential_areas(self, pool, gridded_pop):
        residential_areas = create_residential_areas_from_gridded_pop(gridded_pop)
        total_pop = sum([pop for name, coords, pop, outline in residential_areas])
        return [ResidentialArea(name,
                                coords,
                                # population inside the residential area :
                                round(pop / total_pop * self.population),
                                self,
                                outline)
                for name, coords, pop, outline in residential_areas]

    def create_places(self, pool):
        places = sum([get_places(pool, g) for g in self.districts], [])
        return [Place(
            p["name"],
            p["mass"],
            [p["lat"], p["lon"]],
            p["type_name"],
            p["type_name_fr"],
            p["category_name"],
            p["category_name_fr"],
            p["reason_name"],
            p["reason_name_fr"],
            p["characteristic"]
        ) for p in places]

    def create_cluster_areas(self):
        cluster_areas = []
        places = pd.DataFrame({"category": [p.category for p in self.places],
                               "place": self.places})
        categories = places["category"].drop_duplicates()

        def create_cluster(places, commune, clustering_distance):
            return [ClusterArea(places, commune)]
            """
            places_coords = [p.coords for p in places]
            if len(places_coords) > 1:
                cluster_labels = cluster_single(places_coords, clustering_distance)
                clusters = split_clustered_data(places, cluster_labels)
                return [ClusterArea(c, commune) for c in clusters]
            else:
                return [ClusterArea(places, commune)]"""

        [cluster_areas.extend(create_cluster(places.loc[places["category"] == category, "place"].to_list(),
                                             self,
                                             self.clustering_distance))
         for category in categories]
        return cluster_areas

    def presentation(self):
        print(f"--- Commune {self.name} ({self.postal_code}) ---")
        print(f"- population : {self.population}")
        print(f"- jobs number : {self.jobs_nb}")
        print(f"- status : {self.status}")
        # print(f"- flows home work : {self.flows_home_work}")
        # [ra.presentation() for ra in self.residential_areas]
        # [wa.presentation() for wa in self.work_areas]
        # [p.presentation() for p in self.places]
        [ca.presentation() for ca in self.cluster_areas]
        [hh.presentation() for hh in self.households]
        pprint.pprint(self.to_dict_output())

    def to_dict_output(self):
        return {
            "geo_code": self.geo_code,
            "name": self.name,
            "center": self.coords,
            "population": self.population,
            "status": self.status,
        }


class ResidentialCommune(Commune):

    def __init__(self, pool, geo_code, zone):
        Commune.__init__(self, pool, geo_code)
        print(self.name)
        #time.sleep(1)
        self.outline = get_commune_outline(pool, geo_code)
        self.aav = get_aav(pool, geo_code)
        self.epci_code = get_epci(pool, geo_code)

        self.gridded_population = sum([get_gridded_population(pool, g) for g in self.districts], [])
        self.csp = get_csp(pool, geo_code)
        self.pop_age = get_pop_age_nb(pool, geo_code)

        self.households_cars_nb = get_households_cars_nb(pool, geo_code)
        self.critair = get_critair(pool, self.districts)
        self.gini = get_gini(pool, geo_code)
        self.decile_ratio = get_decile_ratio(pool, geo_code)
        self.median_income = get_median_income(pool, geo_code)
        self.precariousness = get_precariousness_prop(pool, geo_code)

        self.flows_prop_by_geo_code, self.flows_prop_by_mode_geo_code, self.flows_prop_by_mode, self.flows_prop_by_geo_code_mode = get_flows_home_work_trans(pool, geo_code)

        self.surface = get_surface(pool, geo_code)
        self.artificialization_rate = get_artificialization_rate(pool, geo_code)
        self.density = round(self.population / self.surface)
        self.corrected_density = round(self.density / self.artificialization_rate * 100) \
            if self.artificialization_rate != 0 else None

        self.zone = zone
        if True: # self.population < 5:
            self.residential_areas = self.create_residential_areas(pool, self.gridded_population)
        else:
            self.residential_areas = [ResidentialArea(self.name,
                                                      self.coords,
                                                      self.population,
                                                      self,
                                                      self.outline)]
        self.work_areas = [WorkArea(self.name, self.coords, self.jobs_nb, self)]
        self.places = self.create_places(pool)

        self.cluster_areas = self.create_cluster_areas()

    def to_dict_output(self):
        return {
            "geo_code": self.geo_code,
            "name": self.name,
            "outline": self.outline,
            "aav": self.aav,
            "epci_code": self.epci_code,
            "zone": self.zone,
            "center": self.coords,
            "population": self.population,
            "gridded_population": self.gridded_population,
            "status": self.status,
            "csp": self.csp,
            "pop_age": self.pop_age,
            "jobs_nb": self.jobs_nb,
            "workers_within_commune_prop": self.workers_within_commune_prop,
            "flows_home_work": {flows[0]: flows[4] for flows in self.flows_home_work},
            "flows_home_work_workers": {flows[0]: {"coords" : [flows[2], flows[3]], "name": flows[1], "flow": flows[4]} for flows in self.flows_home_work_workers},
            "gini": self.gini,
            "median_income": self.median_income,
            "decile_ratio": self.decile_ratio,
            "precariousness": self.precariousness,
            "density": self.density,
            "corrected_density": self.corrected_density,
            "motorisation_rate": round(100 * (1 - self.households_cars_nb["0"] / sum(self.households_cars_nb.values())),
                                       1),
            "critair": self.critair,
            "cycle_paths_length": self.cycle_paths_length,
            "cycle_paths_length_per_hab": self.cycle_paths_length_per_hab,
            "residential_areas": [{
                "id": ra.id,
                "coords": ra.coords,
                "name": ra.name,
                "population": ra.mass,
                "outline": ra.outline
            } for ra in self.residential_areas],
            "cluster_areas": [{
                "id": ra.id,
                "name": ra.name,
                "category": ra.category,
                "outline": ra.outline
            } for ra in self.cluster_areas]
        }


class InfluenceCommune(Commune):

    def __init__(self, pool, geo_code):
        Commune.__init__(self, pool, geo_code, CLUSTERING_DISTANCE_INFLUENCE)
        print(self.name)
        self.work_areas = [WorkArea(self.name, self.coords, self.jobs_nb, self)]
        self.places = self.create_places(pool)
        self.cluster_areas = self.create_cluster_areas()


class WorkCommune(Commune):

    def __init__(self, pool, geo_code):
        Commune.__init__(self, pool, geo_code, CLUSTERING_DISTANCE_INFLUENCE)
        print(self.name)
        self.work_areas = [WorkArea(self.name, self.coords, self.jobs_nb, self)]
        self.places = self.create_places(pool)
        self.cluster_areas = self.create_cluster_areas()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    ResidentialCommune(None, 79048, 1).presentation()

