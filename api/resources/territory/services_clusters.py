import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Transformer

from api.resources.common.clustering import cluster_single, cluster_ward
from api.resources.common.cog import COG
from api.resources.common.log_stats import log_stats
from api.resources.common.util_territory import get_neighbors, get_work_communes
from data_manager.insee_bpe.places_categories import get_places_categories
from data_manager.sources.sources import get_years_for_source, get_label_link_for_source_year

from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request

source_label = "insee_bpe"

dataset_services_cluster = {
    "endpoint": "territory/services_cluster",
    "is_mesh_element": False,
    "meshes": None,
    "name_year": "INSEE BPE",
    "years": get_years_for_source(source_label),
}


def get_bpe_places_no_schools(geo_codes, year):
    result = db_request(
        """SELECT insee_bpe.id, p.CODGEO_DES,
                    types.name, insee_bpe_types.name, insee_bpe_types.daily_visitors, 
                    categories.name, reasons.name, 
                    insee_bpe.lat, insee_bpe.lon 
            FROM insee_bpe 
            JOIN insee_passage_cog AS p ON insee_bpe.geo_code = p.CODGEO_INI
            
            JOIN insee_bpe_types ON insee_bpe.id_type = insee_bpe_types.id
            JOIN types ON insee_bpe_types.id_type = types.id
            JOIN categories ON types.id_category = categories.id
            JOIN reasons ON categories.id_reason = reasons.id
            
            WHERE p.CODGEO_DES IN :geo_codes
            AND insee_bpe.year_data = :year_data
            AND insee_bpe_types.to_keep = 1 
            AND categories.id != 1
            AND p.year_cog = :cog
        """,
        {
            "geo_codes": geo_codes,
            "year_data": year,
            "cog": COG
        }
    )
    bpe_places = pd.DataFrame(result, columns=["id", "geo_code",
                                               "type", "type_fr", "mass",
                                               "category", "reason",
                                               "lat", "lon"])
    return bpe_places


def get_schools(geo_codes, year):
    result = db_request(
        """SELECT e.id, p.CODGEO_DES, 
                types.name, t.name, t.daily_visitors, 
                categories.name, reasons.name, 
                e.lat, e.lon 
            FROM educationdatagouv_schools AS e
            JOIN insee_passage_cog AS p ON e.geo_code = p.CODGEO_INI
            
            JOIN educationdatagouv_schools_types AS t ON e.id_type = t.id
            JOIN types ON t.id_type = types.id
            JOIN categories ON types.id_category = categories.id
            JOIN reasons ON categories.id_reason = reasons.id
            
            WHERE p.CODGEO_DES IN :geo_codes
            AND e.year_data = :year_data
            AND t.to_keep = 1 
            AND p.year_cog = :cog
        """,
        {
            "geo_codes": geo_codes,
            "year_data": year,
            "cog": COG
        }
    )

    schools = pd.DataFrame(result, columns=["id", "geo_code",
                                            "type", "type_fr", "mass",
                                            "category", "reason",
                                            "lat", "lon"])
    return schools


def get_universities(geo_codes, year):
    result = db_request(
        """SELECT univ.id, p.CODGEO_DES,
                types.name, univ_types.name_univ_type, univ.student_nb, 
                categories.name, reasons.name, 
                univ.lat, univ.lon 
            FROM esrdatagouv_universities AS univ 
            JOIN insee_passage_cog AS p ON univ.geo_code = p.CODGEO_INI
            
            JOIN esrdatagouv_universities_types AS univ_types ON univ.code_type = univ_types.id_univ_type
            JOIN types  ON univ_types.id_type = types.id
            JOIN categories ON types.id_category = categories.id
            JOIN reasons ON categories.id_reason = reasons.id
            
            WHERE p.CODGEO_DES IN :geo_codes
            AND univ.year_data = :year_data
            AND p.year_cog = :cog
        """,
        {
            "geo_codes": geo_codes,
            "year_data": year,
            "cog": COG
        }
    )
    universities = pd.DataFrame(result, columns=["id", "geo_code",
                                                 "type", "type_fr", "mass",
                                                 "category", "reason",
                                                 "lat", "lon"])

    universities["mass"] = universities["mass"].fillna(50)

    return universities


def format_all_places(bpe_places, schools, universities):
    places = pd.concat([bpe_places, schools, universities])
    places.dropna(subset=["lat", "lon"], inplace=True)

    places["coords_geo"] = [[lon, lat] for lat, lon in zip(places["lat"], places["lon"])]

    # Geo to Lambert93 coordinates system :
    transformer2154 = Transformer.from_crs("epsg:4326",  # World Geodetic System (lat/lon)
                                           "epsg:2154")  # Lambert 93 (x, y)

    def geo_to_lambert(lat, lon):
        x, y = transformer2154.transform(lat, lon)
        return [round(x), round(y)]

    places["coords_lamb"] = [geo_to_lambert(lat, lon) for lat, lon in zip(places["lat"], places["lon"])]
    return places


def create_clusters_typology(places):
    places_categories = get_places_categories()
    categories = places_categories[["name", "characteristic_level_0",
                                    "characteristic_level_1", "characteristic_level_2"]]

    places["nb_types_by_category"] = places.groupby(["labels", "category"], as_index=False)[["type"]].transform(
        lambda types: len(types.drop_duplicates())
    )

    clusters_categories = places.drop_duplicates(subset=["labels", "category"])\
        .groupby("labels", as_index=True)[["category", "nb_types_by_category"]]\
        .apply(
        lambda df: pd.merge(categories, df, left_on="name", right_on="category", how="left").fillna(0)
    )
    clusters_categories["characteristic_level_0"] = \
        clusters_categories["nb_types_by_category"] >= clusters_categories["characteristic_level_0"]
    clusters_categories["characteristic_level_1"] = \
        clusters_categories["nb_types_by_category"] >= clusters_categories["characteristic_level_1"]
    clusters_categories["characteristic_level_2"] = \
        clusters_categories["nb_types_by_category"] >= clusters_categories["characteristic_level_2"]

    def typology_rules(cluster):
        label = cluster.index[0][0]
        if cluster["characteristic_level_2"].sum() == len(cluster):
            return 2
        elif cluster["characteristic_level_1"].sum() >= len(cluster) - 1 or (places["labels"] == label).sum() > 40:
            return 1
        elif cluster["characteristic_level_0"].sum() >= len(cluster) - 1 and (places["labels"] == label).sum() > 3:
            return 0
        else:
            return None

    clusters_typology = clusters_categories.groupby("labels").apply(typology_rules).rename("typology")
    return clusters_typology


def create_clusters(places, clustering_distance_single=250,
                    clustering_distance_ward=300**2, min_nb_of_items_inside_cluster=3):
    # 250 : distance séparant chaque cluster "global"
    # 300 : écart type de la distance entre les points du cluster "local"



    """places["labels_global"] = places.groupby("geo_code")[["coords_lamb"]].transform(
        lambda x: cluster_single(x.tolist(), clustering_distance_single)
    )
    places["labels_global"] = places["geo_code"] + "_" + places["labels_global"].astype(str)

    places["labels_local"] = places.groupby("labels_global")[["coords_lamb"]].transform(
        lambda x: cluster_ward(x.tolist(), clustering_distance_ward)
    )
    places["labels"] = places["labels_global"].astype(str) + "_" + places["labels_local"].astype(str)

    places.drop(columns=["labels_global", "labels_local"], inplace=True)"""

    places["labels"] = places["geo_code"]

    # filter small clusters
    places = places.groupby("labels", as_index=False).filter(lambda df: len(df) > min_nb_of_items_inside_cluster)

    # create clusters
    clusters = places.groupby("labels", as_index=False).agg(
        **{
            "geo_code": pd.NamedAgg(column="geo_code", aggfunc="first"),
            "coords_geo": pd.NamedAgg(column="coords_geo", aggfunc=lambda x: list(np.round(np.mean(x.tolist(), axis=0), decimals=5))),
            "places_nb": pd.NamedAgg(column="geo_code", aggfunc="count"),
        }
    )
    clusters["places"] = places.groupby("labels").apply(
        lambda df: " - ".join([f"{nb} {name.lower()}" for name, nb in df["type_fr"].value_counts().items()])
    ).to_list()
    cluster_typology = create_clusters_typology(places)
    clusters = pd.merge(clusters, cluster_typology, left_on="labels", right_index=True)

    # filter clusters
    clusters = clusters.dropna(subset=["typology"])

    if __name__ == '__main__':
        places.groupby("labels").apply(
            lambda df: plt.plot([c[1] for c in df["coords_geo"]], [c[0] for c in df["coords_geo"]], 'o', markersize=2)
        )
        plt.plot([c[1] for c in clusters["coords_geo"]], [c[0] for c in clusters["coords_geo"]], 'x', markersize=4)
        plt.axis('equal')
        plt.show()

    return clusters


def get_services_cluster(geo_codes, year):
    sources = [get_label_link_for_source_year(name, year) for name in [source_label]] + \
              [get_label_link_for_source_year("educationdatagouv_schools", "2024")] + \
              [get_label_link_for_source_year("esrdatagouv_universities", "2017")]

    influence_geocodes = get_neighbors(geo_codes)
    #work_geocodes = get_work_communes(geo_codes, influence_geocodes)
    all_geocodes = geo_codes + influence_geocodes # + work_geocodes

    bpe_places = get_bpe_places_no_schools(all_geocodes, year)
    schools = get_schools(all_geocodes, get_years_for_source("educationdatagouv_schools")[0])
    universities = get_universities(all_geocodes, get_years_for_source("esrdatagouv_universities")[0])

    all_places = format_all_places(bpe_places, schools, universities)

    clusters = create_clusters(all_places)
    clusters = clusters.replace({np.nan: None})

    return {
        "elements": {
            "services_clusters": {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {
                        "coordinates": coords,
                        "places_nb": places_nb,
                        "places": places,
                        "typology": typology,
                        "geo_code": geo_code,
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": coords
                    }
                } for coords, places_nb, places, typology, geo_code in zip(
                    clusters["coords_geo"],
                    clusters["places_nb"],
                    clusters["places"],
                    clusters["typology"],
                    clusters["geo_code"],
                )]
            }},
        # "legend": legend.to_dict(orient="list"),
        "sources": sources,
        "is_mesh_element": False
    }


class ServicesCluster(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes
        year = perimeter.year

        log_stats("services_cluster", geo_codes, None, year)
        message_request("services_cluster", geo_codes)
        return get_services_cluster(geo_codes, year)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    print(get_services_cluster(["75056"], "2021"))
