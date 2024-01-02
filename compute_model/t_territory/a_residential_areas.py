import pandas as pd
import numpy as np
from pyproj import Transformer

from compute_model.v_database_connection.db_request import db_request
from compute_model.u_utilities.a_clustering import cluster_single, split_clustered_data, cluster_ward, display_clusters
from compute_model.sources import sources


def get_gridded_population(geo_codes, source=sources["gridded_pop"]["year"]):
    result = db_request(
        """ SELECT geo_code, idGrid200, Ind, Men
            FROM insee_filosofi_gridded_pop 
            WHERE geo_code IN :geo_codes AND year_data = :year_data
        """,
        {
            "geo_codes": geo_codes,
            "year_data": source
        }
    )
    gridded_population = pd.DataFrame(result, columns=["geo_code", "idGrid200", "population", "households"], dtype=str)

    # Europe to Geodetic coordinates system :
    transformer4326 = Transformer.from_crs("epsg:3035",  # Système Inspire
                                           "epsg:4326")  # World Geodetic System (lat/lon)
    # Europe to Lambert93 coordinates system :
    transformer2154 = Transformer.from_crs("epsg:3035",  # Système Inspire
                                           "epsg:2154")  # Lambert 93 (x, y)

    def europe_to_geo(x, y):
        lat, lon = transformer4326.transform(x, y)
        return [lat, lon]

    def europe_to_lambert(x, y):
        x_l, y_l = transformer2154.transform(x, y)
        return [round(x_l), round(y_l)]

    def idToCoordsGeo(id):
        coords = id.split("N")[-1]
        x, y = coords.split("E")
        return europe_to_geo(x, y)

    def idToCoordsLamb(id):
        coords = id.split("N")[-1]
        x, y = coords.split("E")
        return europe_to_lambert(x, y)

    gridded_population["coords_geo"] = gridded_population["idGrid200"].apply(lambda id: idToCoordsGeo(id))
    gridded_population["coords_lamb"] = gridded_population["idGrid200"].apply(lambda id: idToCoordsLamb(id))
    gridded_population = gridded_population.astype({"population": "float",
                                                    "households": "float"})
    gridded_population.drop(columns="idGrid200", inplace=True)
    return gridded_population


def get_missing_gridded_population(geo_codes, year_data=sources["dossier_complet"]["year"]):
    result = db_request("""
                SELECT dc.CODGEO, dc.POP, dc.MEN, ign.centroid_lat, ign.centroid_lon
                FROM insee_dossier_complet AS dc
                JOIN ign_commune_center AS ign ON dc.CODGEO = ign.geo_code
                WHERE dc.CODGEO IN :geo_codes AND dc.year_data = :year_data
        """,
        {
            "geo_codes": geo_codes,
            "year_data": year_data
        }
    )
    pop = pd.DataFrame(result, columns=["geo_code", "population", "households", "lat", "lon"])

    # Geo to Lambert93 coordinates system :
    transformer2154 = Transformer.from_crs("epsg:4326",  # Système Inspire
                                           "epsg:2154")  # Lambert 93 (x, y)

    def geo_to_lambert(lat, lon):
        x_l, y_l = transformer2154.transform(lat, lon)
        return [round(x_l), round(y_l)]

    pop["coords_geo"] = [[lat, lon] for lat, lon in zip(pop["lat"], pop["lon"])]
    pop["coords_lamb"] = [geo_to_lambert(lat, lon) for lat, lon in zip(pop["lat"], pop["lon"])]

    pop = pop.astype({"population": "float", "households": "float"})
    pop.drop(columns=["lat", "lon"], inplace=True)

    return pop


def get_population(geo_codes, year_data=sources["dossier_complet"]["year"]):
    result = db_request("""
                SELECT CODGEO, POP
                FROM insee_dossier_complet 
                WHERE CODGEO IN :geo_codes AND year_data = :year_data
        """,
        {
            "geo_codes": geo_codes,
            "year_data": year_data
        }
    )
    pop = pd.DataFrame(result, columns=["geo_code", "population"])
    return pop


def create_gridded_pop_cluster(gridded_pop, global_threshold_m, local_threshold_m):
    gridded_pop["labels_global"] = gridded_pop.groupby("geo_code")[["coords_lamb"]].transform(
        lambda x: cluster_single(x.tolist(), global_threshold_m)
    )
    gridded_pop["labels_global"] = gridded_pop["geo_code"] + "_" + gridded_pop["labels_global"].astype(str)

    gridded_pop["labels_local"] = gridded_pop.groupby("labels_global")[["coords_lamb"]].transform(
        lambda x: cluster_ward(x.tolist(), local_threshold_m)
    )
    gridded_pop["labels"] = gridded_pop["labels_global"].astype(str) + "_" + gridded_pop["labels_local"].astype(str)

    gridded_pop.drop(columns=["labels_global", "labels_local"], inplace=True)
    return gridded_pop


def get_residential_areas(geo_codes):
    residential_areas = []
    gridded_pop = get_gridded_population(geo_codes)
    missing_gridded_pop_geo_codes = [g for g in geo_codes if g not in gridded_pop["geo_code"].tolist()]
    if len(missing_gridded_pop_geo_codes) > 0:
        missing_gridded_pop = get_missing_gridded_population(missing_gridded_pop_geo_codes)
        gridded_pop = pd.concat([gridded_pop, missing_gridded_pop])

    pop = get_population(geo_codes)

    # Parameters for global clustering (villages) - do not change
    global_threshold_m = 250  # meters
    # Parameters for local clustering (dense areas) - do not change
    local_threshold_m = 5000  # meters
    # Min number of population to keep a cluster
    min_nb_of_population_inside_cluster = 20

    clustered_gridded_pop = create_gridded_pop_cluster(gridded_pop,
                                          global_threshold_m,
                                          local_threshold_m)

    # create residential areas frame attributes
    residential_areas = clustered_gridded_pop.groupby("labels", as_index=False).agg(
        **{
            "geo_code": pd.NamedAgg(column="geo_code", aggfunc="first"),
            "coords_geo": pd.NamedAgg(column="coords_geo", aggfunc=lambda x: list(np.mean(x.tolist(), axis=0))),
            "coords_lamb": pd.NamedAgg(column="coords_lamb", aggfunc=lambda x: list(np.round(np.mean(x.tolist(), axis=0)))),
            "inner_dist": pd.NamedAgg(column="coords_lamb", aggfunc=lambda x: np.round(np.sqrt(np.prod(np.std(x.tolist(), axis=0))))),
            "pop": pd.NamedAgg(column="population", aggfunc="sum"),
        }
    )

    # filter residential areas with few people
    mask_low_pop = residential_areas["pop"] < min_nb_of_population_inside_cluster
    mask_highest_pop = residential_areas.groupby("geo_code", as_index=False)["pop"].transform(lambda s: s.idxmax() == s.index)["pop"]
    residential_areas = residential_areas[~mask_low_pop | mask_highest_pop]

    # adjust population to fit with total pop of commune
    residential_areas = pd.merge(residential_areas, pop, on="geo_code", how="left")
    residential_areas["pop"] = residential_areas.groupby("geo_code")[["pop"]].transform(lambda pop: pop / pop.sum())
    residential_areas["pop"] = residential_areas["pop"].mul(residential_areas["population"]).round()
    residential_areas["category"] = "residential"
    residential_areas["reason"] = "residential"
    residential_areas.drop(columns=["population"], inplace=True)
    residential_areas.rename(columns={"labels": "id", "pop": "mass"}, inplace=True)

    if __name__ == "__main__":
        clusters = clustered_gridded_pop.groupby("labels").apply(lambda df: df["coords_lamb"].tolist()).tolist()
        display_clusters(clusters, residential_areas["coords_lamb"])

    return residential_areas


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 60)
    pd.set_option('display.width', 4000)

    print(get_residential_areas(["29084", "29040"]))
    print(get_residential_areas(["01004", "01002"]))

