import pandas as pd

from model.data_analysis.territory_analysis import get_areas_by_reason, get_areas_by_category, build_activity_zones
from model.data_analysis.travels_analysis import get_travels_analysis
from model.territory import Territory


class TerritoryOutput:
    def __init__(self, territory):
        """
        Constructor.
        :param territory: (Territory)
        """

        # GENERAL
        self.name = territory.name

        self.population = sum([c.population for c in territory.communes])
        self.households_nb = sum([sum(c.households_cars_nb.values()) for c in territory.communes])
        self.jobs_nb = sum([c.jobs_nb for c in territory.communes])

        self.motorisation_rate = round(
            100 * (1 - sum([c.households_cars_nb["0"] for c in territory.communes]) / self.households_nb))
        self.density = round(self.population / sum([c.surface for c in territory.communes]))

        self.pop_status = sum_pop_status(territory)

        self.sources = territory.sources

        # COMMUNES
        self.communes = [c.to_dict_output() for c in territory.communes]
        self.influence_communes = [c.to_dict_output() for c in territory.influence_communes]
        self.work_communes = [c.to_dict_output() for c in territory.work_communes]

        # TRAVELS
        if hasattr(territory, 'synthetic_population') & hasattr(territory, 'travels_demand'):
            self.travels_analysis = get_travels_analysis(territory.travels_demand,
                                                         territory.synthetic_population,
                                                         territory)

        if(hasattr(territory, 'geo_zones')):
            self.geo_code_dict = territory.geo_zones.drop(columns=["geometry"]).drop_duplicates(subset="geo_code").\
                set_index("geo_code").to_dict(orient="index")

        # PROFILES
        #self.profiles = get_profiles(territory.synthetic_population, territory.travels_demand, territory)

        # COMMUTER MATRIX
        geo_code_to_name = {c.geo_code: c.name for c in territory.communes}
        if hasattr(territory, 'commuter_matrix'):
            self.commuter_matrix = territory.commuter_matrix.transpose().rename(columns=geo_code_to_name).to_dict("index")

        # AREAS
        not_residential_areas = [area for area in territory.all_areas if area.category != "residential"]
        self.areas_by_reason = get_areas_by_reason(not_residential_areas)
        self.areas_by_category = get_areas_by_category(not_residential_areas)

        self.places = [p.__dict__ for p
                       in sum([c.places for c in territory.communes + territory.influence_communes + territory.work_communes], [])]
        self.areas = [area.to_dict_output() for area
                      in territory.all_areas if area.category != "residential"]

        # CHARACTERISTIC ACTIVITY CLUSTER
        self.activity_cluster = [ca.to_dict_output() for ca in build_activity_zones(territory)]

        # Public transport
        self.public_transport = [pt.to_dict() for pt in territory.public_transport]
        self.cycle_paths = pd.concat([c.cycle_paths for c in territory.communes + territory.influence_communes]).to_dict(orient="records")
        self.cycle_parkings = pd.concat([c.cycle_parkings for c in territory.communes + territory.influence_communes]).to_dict(orient="records")
        self.irve = pd.concat([c.irve for c in territory.communes + territory.influence_communes]).to_dict(orient="records")
        self.bnlc = pd.concat([c.bnlc for c in territory.communes + territory.influence_communes]).to_dict(orient="records")
        self.railways = territory.railways
        self.zfe = territory.zfe.to_dict(orient="records")


def sum_pop_status(territory):
    status = {}

    def add(key, value):
        if key not in status.keys():
            status[key] = value
        else:
            status[key] += value

    [[add(key, value) for key, value in c.status.items()] for c in territory.communes]
    return status


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)

    territory_test = Territory("test", ["79048"], [])
    output = TerritoryOutput(territory_test)
    print(output.__dict__)
