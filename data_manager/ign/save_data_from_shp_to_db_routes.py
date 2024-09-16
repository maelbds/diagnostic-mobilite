"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import os

import pandas as pd
import shapefile
from shapely import wkb, prepare, crosses
from shapely.ops import transform, linemerge
from pyproj import Transformer

from shapely.geometry import shape, GeometryCollection

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.db_functions import load_database


# geometry to wkb
from data_manager.ign.commune_outline import read_shp_outlines_communes


def shape_to_wkb_geometry_collection(shape):
    geom_coll = GeometryCollection([shape])
    geom_wkb = wkb.dumps(geom_coll)
    return geom_wkb


def read_shp_outlines_routes():
    print("Reading data routes : nationale, autoroute")
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    sf = shapefile.Reader(
        "data/ROUTE500_3-0__SHP_LAMB93_FXX_2021-11-03/ROUTE500/1_DONNEES_LIVRAISON_2022-01-00175/R500_3-0_SHP_LAMB93_FXX-ED211/RESEAU_ROUTIER/TRONCON_ROUTE",
        encoding="latin-1")

    records = sf.records()

    routes = pd.DataFrame([{
        "ID_RTE500": s["ID_RTE500"],
        "VOCATION": s["VOCATION"],
        "NUM_ROUTE": s["NUM_ROUTE"],
        "CLASS_ADM": s["CLASS_ADM"],
        "NB_CHAUSSE": s["NB_CHAUSSE"],
        "NB_VOIES": s["NB_VOIES"],
        "SENS": s["SENS"]
    } for s in records])

    mask_class_adm = routes["CLASS_ADM"].isin(["Nationale", "Autoroute"]) #, "Nationale", "Départementale", "Autoroute"])
    routes = routes[mask_class_adm]

    transformer = Transformer.from_crs("epsg:2154", "epsg:4326")
    def to_wgs(x, y):
        return reversed(transformer.transform(x, y))

    routes["geometry_shape_WGS"] = [transform(to_wgs, shape(sf.shape(i).__geo_interface__)) for i in routes.index]
    return routes


def save_data(data, database_name):
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ")"

    def request(cur, cols):
        cur.execute("""INSERT INTO  """ + database_name + " " + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

    conn.commit()
    conn.close()


def handle_routes():
    routes = read_shp_outlines_routes()

    routes["geometry"] = [shape_to_wkb_geometry_collection(r) for r in routes["geometry_shape_WGS"]]
    routes.drop(columns=["geometry_shape_WGS"], inplace=True)
    routes["year_data"] = "2021"
    routes.drop_duplicates(subset=["ID_RTE500"], inplace=True)
    print(routes)
    return routes


def handle_routes_communes():
    routes = read_shp_outlines_routes()
    communes = read_shp_outlines_communes()

    [prepare(s) for s in communes["outline"]]

    def agg_func(df):
        return pd.Series({
            "geometry": linemerge(df["geometry_shape_WGS"])
        })
    routes_s = routes.groupby("NUM_ROUTE", as_index=False).apply(agg_func)
    [prepare(s) for s in routes_s["geometry"]]
    print("routes grouped by line")

    routes_s["communes"] = [[code_commune for code_commune, outline_commune
                           in zip(communes["geo_code"], communes["outline"])
                           if crosses(r_shape, outline_commune)]
                          for r_shape in routes_s["geometry"]]
    print("routes by commune found")

    communes_routes = []
    [communes_routes.append(pd.DataFrame({
        "CODGEO": [g for g in geo_codes],
        "NUM_ROUTE": [num_route for g in geo_codes],
    })) for num_route, geo_codes in zip(routes_s["NUM_ROUTE"], routes_s["communes"])]
    communes_routes = pd.concat(communes_routes)

    communes_routes["year_data"] = "2021"
    communes_routes["year_cog"] = "2022"
    print("communes routes :")
    print(communes_routes)

    return communes_routes


def load_routes(pool, table_name):
    data = handle_routes()

    cols_table = {
        "ID_RTE500": "VARCHAR(50) NOT NULL",
        "VOCATION": "VARCHAR(50) NOT NULL",
        "NUM_ROUTE": "VARCHAR(50) NOT NULL",
        "CLASS_ADM": "VARCHAR(50) NOT NULL",
        "NB_CHAUSSE": "VARCHAR(50) NOT NULL",
        "NB_VOIES": "VARCHAR(50) NOT NULL",
        "SENS": "VARCHAR(50) NOT NULL",
        "geometry": "GEOMETRYCOLLECTION NULL DEFAULT NULL",

        "year_data": "VARCHAR(20) NOT NULL",
    }
    keys = "PRIMARY KEY (ID_RTE500, year_data) USING BTREE, KEY (NUM_ROUTE) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


def load_routes_communes(pool, table_name):
    data = handle_routes_communes()

    cols_table = {
        "CODGEO": "VARCHAR(50) NOT NULL",
        "NUM_ROUTE": "VARCHAR(50) NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (CODGEO, NUM_ROUTE, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    routes = handle_routes()
    communes_routes = handle_routes_communes()

    # to prevent from unuseful loading data
    security = True
    if not security:
        save_data(communes_routes, "ign_routes_communes")
        save_data(routes, "ign_routes")
