import os
import time
import numpy as np

import pandas as pd
from pyproj import Transformer

from data_manager.database_connection.sql_connect import mariadb_connection
from shapely import Point, distance

from data_manager.db_functions import load_database

categories = {
    "B203": "boulangeries",
    "B301": "librairies",
    "D502": "creches",
    "33": "ecoles",
    "35": "ecoles",
    "36": "ecoles",
    "37": "ecoles",
    "B201": "epiceries",
    "B202": "epiceries",
    "B102": "supermarches",
    "B101": "supermarches",
    "A301": "garages",
    "B316": "station_services",
    "F307": "bibliotheques",
    "A206": "postes",
    "A207": "postes",
    "A208": "postes",
    "D307": "pharmacies",
    "D113": "medecins",
    "D201": "medecins",
    "F113": "terrains",
    "F121": "gymnases",
    "F101": "bassins_de_natation",
}
categories = pd.DataFrame({"type_id": categories.keys(), "cat": categories.values()})


def get_gridded_pop(pool, dep):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT grid.idGrid200, grid.Ind, grid.geo_code
                   FROM insee_filosofi_gridded_pop AS grid
                   JOIN insee_cog_communes AS cog ON cog.COM = grid.geo_code
                   WHERE cog.DEP = ?
                        """, [dep])
    result = list(cur)
    conn.close()
    gridded_pop = pd.DataFrame(result, columns=["idGrid200", "pop", "geo_code"])

    print(gridded_pop)

    # Lambert to Geodetic coordinates system :
    transformer = Transformer.from_crs("epsg:3035",  # Système Inspire
                                       "epsg:2154")  # Lambert

    def laea_to_lambert(x, y):
        x_l, y_l = transformer.transform(x, y)
        return [round(x_l), round(y_l)]

    def idToCoords(id):
        coords = id.split("N")[-1]
        x, y = coords.split("E")
        return laea_to_lambert(x, y)

    gridded_pop["coords"] = [idToCoords(id) for id in gridded_pop["idGrid200"]]
    gridded_pop["point"] = [Point(lat, lon) for lat, lon in gridded_pop["coords"]]
    gridded_pop = gridded_pop.astype({"pop": "float"})

    return gridded_pop


def get_bpe(pool, bounds):
    # Lambert to Geodetic coordinates system :
    transformer = Transformer.from_crs("epsg:4326",  # World Geodetic System (lat/lon)
                                       "epsg:2154")  # Lambert

    def geo_to_lambert(x, y):
        lat, lon = transformer.transform(x, y)
        return [round(lat), round(lon)]

    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT insee_bpe.id, insee_bpe.geo_code, 
                    insee_bpe.id_type, insee_bpe_types.name, 
                    insee_bpe.lat, insee_bpe.lon 
                FROM insee_bpe 
                JOIN insee_bpe_types 
                ON insee_bpe.id_type = insee_bpe_types.id
                WHERE insee_bpe.lat > ? 
                AND insee_bpe.lat < ?
                AND insee_bpe.lon > ?
                AND insee_bpe.lon < ?
                """,
                [bounds["min_lat"] - 0.2,
                 bounds["max_lat"] + 0.2,
                 bounds["min_lon"] - 0.2,
                 bounds["max_lon"] + 0.2])
    result = list(cur)
    conn.close()

    bpe_places = pd.DataFrame(result, columns=["id", "geo_code",
                                               "type_id", "type_name_fr",
                                               "lat", "lon"])
    bpe_places.dropna(subset=["lat", "lon"], inplace=True)
    bpe_places["coords"] = [geo_to_lambert(lat, lon) for lat, lon in zip(bpe_places["lat"], bpe_places["lon"])]
    bpe_places["point"] = [Point(x, y) for x, y in bpe_places["coords"]]
    bpe_places["x"] = [p.x for p in bpe_places["point"]]
    bpe_places["y"] = [p.y for p in bpe_places["point"]]
    bpe_places.drop(columns=["lat", "lon"], inplace=True)

    bpe_places = pd.merge(bpe_places, categories, on="type_id")

    return bpe_places


def get_schools(pool, bounds):
    # Lambert to Geodetic coordinates system :
    transformer = Transformer.from_crs("epsg:4326",  # World Geodetic System (lat/lon)
                                       "epsg:2154")  # Lambert

    def geo_to_lambert(x, y):
        lat, lon = transformer.transform(x, y)
        return [round(lat), round(lon)]

    conn = mariadb_connection(None)
    cur = conn.cursor()
    cur.execute("""SELECT s.id, s.geo_code, 
                    st.id_type, s.name, 
                    s.lat, s.lon 
                FROM educationdatagouv_schools AS s
                JOIN educationdatagouv_schools_types AS st
                ON s.id_type = st.id
                WHERE s.lat > ? 
                AND s.lat < ?
                AND s.lon > ?
                AND s.lon < ?
                """,
                [bounds["min_lat"] - 0.2,
                 bounds["max_lat"] + 0.2,
                 bounds["min_lon"] - 0.2,
                 bounds["max_lon"] + 0.2])
    result = list(cur)
    conn.close()

    bpe_places = pd.DataFrame(result, columns=["id", "geo_code",
                                               "type_id", "type_name_fr",
                                               "lat", "lon"])
    bpe_places.dropna(subset=["lat", "lon", "type_id"], inplace=True)
    bpe_places["coords"] = [geo_to_lambert(lat, lon) for lat, lon in zip(bpe_places["lat"], bpe_places["lon"])]
    bpe_places["point"] = [Point(x, y) for x, y in bpe_places["coords"]]
    bpe_places["x"] = [p.x for p in bpe_places["point"]]
    bpe_places["y"] = [p.y for p in bpe_places["point"]]
    bpe_places["type_id"] = bpe_places["type_id"].astype("int").astype("str")
    bpe_places.drop(columns=["lat", "lon"], inplace=True)

    bpe_places = pd.merge(bpe_places, categories, on="type_id")

    return bpe_places


def save_to_db(data):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ")"

    def request(cur, cols):
        cur.execute("""INSERT INTO terristory_services_dist """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

    conn.commit()
    conn.close()


def compute_bounds(gridded_pop):
    bounds_lambert = {
        "min_x": min([c[0] for c in gridded_pop["coords"]]),
        "max_x": max([c[0] for c in gridded_pop["coords"]]),
        "min_y": min([c[1] for c in gridded_pop["coords"]]),
        "max_y": max([c[1] for c in gridded_pop["coords"]]),
    }

    transformer = Transformer.from_crs("epsg:2154",  # World Geodetic System (lat/lon)
                                       "epsg:4326")  # Lambert

    def lambert_to_geo(x, y):
        lat, lon = transformer.transform(x, y)
        return [lat, lon]

    bounds_geo = {}
    bounds_geo["min_lat"], bounds_geo["min_lon"] = lambert_to_geo(bounds_lambert["min_x"], bounds_lambert["min_y"])
    bounds_geo["max_lat"], bounds_geo["max_lon"] = lambert_to_geo(bounds_lambert["max_x"], bounds_lambert["max_y"])

    print(bounds_geo)
    return bounds_geo


def compute_services_dist(pool, dep):
    gridded_pop = get_gridded_pop(pool, dep)
    print(gridded_pop)

    bounds_geo = compute_bounds(gridded_pop)

    bpe = get_bpe(pool, bounds_geo)
    schools = get_schools(pool, bounds_geo)
    services = pd.concat([bpe, schools])
    print(services)

    def crow_fly_dist_to_real(dist_meters):
        dist_km = dist_meters/1000
        # "From crow-fly distances to real distances, or the origin of detours, Heran"
        return dist_km * (1.1 + 0.3 * np.exp(-dist_km / 20))

    for cat in categories["cat"].drop_duplicates():
        print(cat)
        services_cat = services[services["cat"] == cat]
        print(services_cat)

        def mask_services(point):
            radius = 10 * 1000
            mask_x = ((point.x - radius) < services_cat["x"]) & (services_cat["x"] < (point.x + radius))
            mask_y = ((point.y - radius) < services_cat["y"]) & (services_cat["y"] < (point.y + radius))
            while (mask_x & mask_y).sum() < 10:
                radius = radius * 2
                mask_x = ((point.x - radius) < services_cat["x"]) & (services_cat["x"] < (point.x + radius))
                mask_y = ((point.y - radius) < services_cat["y"]) & (services_cat["y"] < (point.y + radius))
            return mask_x & mask_y

        gridded_pop[cat + "_dist"] = [
            crow_fly_dist_to_real(min([distance(p_bpe, p_grid) for p_bpe in
                 services_cat[mask_services(p_grid)]["point"]]))
            for p_grid in gridded_pop["point"]
        ]
        print(gridded_pop)

    print(gridded_pop)

    gridded_pop.drop(columns=["coords", "point"], inplace=True)

    col_dist_names = [cat + "_dist" for cat in categories["cat"].drop_duplicates()]
    gridded_pop[col_dist_names] = gridded_pop[col_dist_names].multiply(gridded_pop["pop"], axis=0)
    print(gridded_pop)

    communes_dist = gridded_pop.groupby("geo_code", as_index=False).sum()
    communes_dist[col_dist_names] = communes_dist[col_dist_names].div(communes_dist["pop"], axis=0).round(2)
    communes_dist.drop(columns=["pop"], inplace=True)
    print(communes_dist)

    return communes_dist


def load_services_dist(pool, table_name):
    cols_table = {
        "geo_code": "VARCHAR(50) NOT NULL",
        "boulangeries_dist": "FLOAT NULL DEFAULT NULL",
        "librairies_dist": "FLOAT NULL DEFAULT NULL",
        "creches_dist": "FLOAT NULL DEFAULT NULL",
        "ecoles_dist": "FLOAT NULL DEFAULT NULL",
        "epiceries_dist": "FLOAT NULL DEFAULT NULL",
        "supermarches_dist": "FLOAT NULL DEFAULT NULL",
        "garages_dist": "FLOAT NULL DEFAULT NULL",
        "station_services_dist": "FLOAT NULL DEFAULT NULL",
        "bibliotheques_dist": "FLOAT NULL DEFAULT NULL",
        "postes_dist": "FLOAT NULL DEFAULT NULL",
        "pharmacies_dist": "FLOAT NULL DEFAULT NULL",
        "medecins_dist": "FLOAT NULL DEFAULT NULL",
        "terrains_dist": "FLOAT NULL DEFAULT NULL",
        "gymnases_dist": "FLOAT NULL DEFAULT NULL",
        "bassins_de_natation_dist": "FLOAT NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (geo_code) USING BTREE"

    for dep in ["03", "63", "15", "43", "42", "69", "01", "38", "26", "07", "73", "74"]:
        data = compute_services_dist(pool, dep)
        load_database(pool, table_name, data, cols_table, keys)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.max_rows', 60)
    pd.set_option('display.width', 4000)


    compute_services_dist("01")







