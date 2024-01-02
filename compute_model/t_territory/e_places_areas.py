import pandas as pd
import numpy as np
from pyproj import Transformer

from compute_model.v_database_connection.db_request import db_request
from compute_model.u_utilities.a_clustering import cluster_ward, display_clusters
from compute_model.sources import sources


def get_bpe_places_no_schools(geo_codes):
    result = db_request(
        """SELECT insee_bpe.id, insee_bpe.geo_code,
                    types.name, insee_bpe_types.daily_visitors, 
                    categories.name, reasons.name, 
                    insee_bpe.lat, insee_bpe.lon 
            FROM insee_bpe 
            JOIN insee_bpe_types ON insee_bpe.id_type = insee_bpe_types.id
            JOIN types ON insee_bpe_types.id_type = types.id
            JOIN categories ON types.id_category = categories.id
            JOIN reasons ON categories.id_reason = reasons.id
            WHERE insee_bpe.geo_code IN :geo_codes 
            AND insee_bpe_types.to_keep = 1 
            AND year_data = :year_data
            AND categories.id != 1
        """,
        {
            "geo_codes": geo_codes,
            "year_data": sources["bpe"]["year"]
        }
    )
    bpe_places = pd.DataFrame(result, columns=["id", "geo_code",
                                               "type", "mass",
                                               "category", "reason",
                                               "lat", "lon"])
    return bpe_places


def get_schools(geo_codes):
    result = db_request(
        """SELECT e.id, e.geo_code, 
                types.name, t.daily_visitors, 
                categories.name, reasons.name, 
                e.lat, e.lon 
            FROM educationdatagouv_schools AS e
            JOIN educationdatagouv_schools_types AS t ON e.id_type = t.id
            JOIN types ON t.id_type = types.id
            JOIN categories ON types.id_category = categories.id
            JOIN reasons ON categories.id_reason = reasons.id
            WHERE e.geo_code IN :geo_codes 
            AND t.to_keep = 1 
            AND year_data = :year_data
        """,
        {
            "geo_codes": geo_codes,
            "year_data": sources["educationdatagouv"]["year"]
        }
    )

    schools = pd.DataFrame(result, columns=["id", "geo_code",
                                            "type", "mass",
                                            "category", "reason",
                                            "lat", "lon"])
    return schools


def get_universities(geo_codes):
    result = db_request(
        """SELECT univ.id, univ.geo_code,
                types.name, univ.student_nb, 
                categories.name, reasons.name, 
                univ.lat, univ.lon 
            FROM esrdatagouv_universities AS univ 
            JOIN esrdatagouv_universities_types AS univ_types ON univ.code_type = univ_types.id_univ_type
            JOIN types  ON univ_types.id_type = types.id
            JOIN categories ON types.id_category = categories.id
            JOIN reasons ON categories.id_reason = reasons.id
            WHERE univ.geo_code IN :geo_codes
            AND univ.year_data = :year_data
        """,
        {
            "geo_codes": geo_codes,
            "year_data": sources["esrdatagouv"]["year"]
        }
    )
    universities = pd.DataFrame(result, columns=["id", "geo_code",
                                                 "type", "mass",
                                                 "category", "reason",
                                                 "lat", "lon"])

    universities["mass"] = universities["mass"].fillna(50)

    return universities


def get_places(geo_codes):
    bpe_places = get_bpe_places_no_schools(geo_codes)
    schools = get_schools(geo_codes)
    universities = get_universities(geo_codes)

    places = pd.concat([bpe_places, schools, universities])

    places.dropna(subset=["lat", "lon"], inplace=True)

    places["coords_geo"] = [[lat, lon] for lat, lon in zip(places["lat"], places["lon"])]

    # Geo to Lambert93 coordinates system :
    transformer2154 = Transformer.from_crs("epsg:4326",  # World Geodetic System (lat/lon)
                                           "epsg:2154")  # Lambert 93 (x, y)

    def geo_to_lambert(lat, lon):
        x, y = transformer2154.transform(lat, lon)
        return [round(x), round(y)]

    places["coords_lamb"] = [geo_to_lambert(lat, lon) for lat, lon in zip(places["lat"], places["lon"])]

    return places


def get_cluster_areas(geo_codes):
    places = get_places(geo_codes)
    all_cluster_areas = []

    local_threshold_m = 5000

    for category, places_g in places.groupby("category"):
        if len(places_g) > 1:
            places_g["labels"] = cluster_ward(places_g["coords_lamb"].tolist(), local_threshold_m)

            cluster_area = places_g.groupby("labels").agg(**{
                "coords_geo": pd.NamedAgg(column="coords_geo", aggfunc=lambda x: list(np.mean(x.tolist(), axis=0))),
                "coords_lamb": pd.NamedAgg(column="coords_lamb", aggfunc=lambda x: list(np.mean(x.tolist(), axis=0))),
                "inner_dist": pd.NamedAgg(column="coords_lamb", aggfunc=lambda x: np.round(np.sqrt(np.prod(np.std(x.tolist(), axis=0))))),
                "mass": pd.NamedAgg(column="mass", aggfunc="sum"),
                "types": pd.NamedAgg(column="type", aggfunc=list),
                "reason": pd.NamedAgg(column="reason", aggfunc="first"),
                "geo_code": pd.NamedAgg(column="geo_code", aggfunc=lambda x: x.mode().iloc[0]),
            })
            cluster_area["category"] = category

            if __name__ == "__main__":
                clusters = places_g.groupby("labels").apply(lambda df: df["coords_lamb"].tolist()).tolist()
                #display_clusters(clusters, cluster_area["coords_lamb"])
        else:
            cluster_area = places_g.loc[:, ["coords_geo", "coords_lamb", "mass", "reason", "geo_code"]]
            cluster_area["category"] = category
            cluster_area["types"] = places_g["type"].apply(lambda x: list(x))
            cluster_area["inner_dist"] = 0

        all_cluster_areas.append(cluster_area)

    all_cluster_areas = pd.concat(all_cluster_areas).reset_index(drop=True)
    all_cluster_areas["id"] = all_cluster_areas.index
    all_cluster_areas["id"] = "ca_" + all_cluster_areas["id"].astype(str)
    all_cluster_areas = all_cluster_areas[["id", "category", "reason", "types", "mass", "coords_geo", "coords_lamb", "inner_dist", "geo_code"]]

    return all_cluster_areas


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)
    print(get_places(["79048"]))
    print(get_bpe_places_no_schools(["79048"]))
    print(get_schools(["79048"]))
    print(get_universities(["79191"]))

    print(get_cluster_areas(["79048", "79191", "79270"]))
