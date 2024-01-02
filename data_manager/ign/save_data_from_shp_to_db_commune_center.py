"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import os

import pandas as pd
import shapefile
import numpy as np

from shapely.geometry import shape

from data_manager.db_functions import load_database
from data_manager.utilities import load_file_ign


def download_files():
    # reference : "https://geoservices.ign.fr/adminexpress"

    files = [{
        "name": "ADMIN-EXPRESS-COG édition 2021 France entière",
        "url": "https://wxs.ign.fr/x02uy2aiwjo9bm8ce5plwqmr/telechargement/prepackage/ADMINEXPRESS-COG_SHP_WGS84G_PACK_2021-05-19$ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19/file/ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19.7z",
        "dir": "data/2021",
        "zip_name": "ign_admin_express_2021.zip",
        "file_name": "ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19/ADMIN-EXPRESS-COG/1_DONNEES_LIVRAISON_2021-05-19/ADECOG_3-0_SHP_WGS84G_FRA/CHFLIEU_COMMUNE.shp",
    }]

    [load_file_ign(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def read_shp_chef_lieu_com():
    sf = shapefile.Reader(
        "data/2021/ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19/ADMIN-EXPRESS-COG/1_DONNEES_LIVRAISON_2021-05-19/ADECOG_3-0_SHP_WGS84G_FRA/CHFLIEU_COMMUNE")

    chef_lieu_center = [r.__geo_interface__ for r in sf.shapeRecords()]
    chef_lieu = pd.DataFrame([{"id_com": c["properties"]["ID_COM"],
                               "chflieu_lat": c["geometry"]["coordinates"][1],
                               "chflieu_lon": c["geometry"]["coordinates"][0]}
                              for c in chef_lieu_center])
    return chef_lieu


def read_shp_chef_lieu_arr():
    sf = shapefile.Reader(
        "data/2021/ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19/ADMIN-EXPRESS-COG/1_DONNEES_LIVRAISON_2021-05-19/ADECOG_3-0_SHP_WGS84G_FRA/CHFLIEU_ARRONDISSEMENT_MUNICIPAL")

    chef_lieu_center = [r.__geo_interface__ for r in sf.shapeRecords()]
    chef_lieu = pd.DataFrame([{"id_com": c["properties"]["ID_COM"],
                               "chflieu_lat": c["geometry"]["coordinates"][1],
                               "chflieu_lon": c["geometry"]["coordinates"][0]}
                              for c in chef_lieu_center])
    return chef_lieu


def read_shp_centroid_com():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    sf = shapefile.Reader(
        "data/2021/ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19/ADMIN-EXPRESS-COG/1_DONNEES_LIVRAISON_2021-05-19/ADECOG_3-0_SHP_WGS84G_FRA/COMMUNE")

    communes_geo = [r.__geo_interface__ for r in sf.shapeRecords()]
    communes = pd.DataFrame([{"id_com": c["properties"]["ID"],
                              "geo_code": c["properties"]["INSEE_COM"],
                              "centroid_lat": shape(c["geometry"]).centroid.y,
                              "centroid_lon": shape(c["geometry"]).centroid.x}
                             for c in communes_geo])
    return communes


def read_shp_centroid_arr():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    sf = shapefile.Reader(
        "data/2021/ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19/ADMIN-EXPRESS-COG/1_DONNEES_LIVRAISON_2021-05-19/ADECOG_3-0_SHP_WGS84G_FRA/ARRONDISSEMENT_MUNICIPAL")

    communes_geo = [r.__geo_interface__ for r in sf.shapeRecords()]
    communes = pd.DataFrame([{"id_com": c["properties"]["ID"],
                              "geo_code": c["properties"]["INSEE_ARM"],
                              "centroid_lat": shape(c["geometry"]).centroid.y,
                              "centroid_lon": shape(c["geometry"]).centroid.x}
                             for c in communes_geo])
    return communes


def get_commune_center():
    chef_lieu_com = read_shp_chef_lieu_com()
    chef_lieu_arr = read_shp_chef_lieu_arr()
    centroid_com = read_shp_centroid_com()
    centroid_arr = read_shp_centroid_arr()

    center_com = pd.merge(centroid_arr, chef_lieu_arr, on="id_com", how="left").drop(columns=["id_com"])
    center_arr = pd.merge(centroid_com, chef_lieu_com, on="id_com", how="left").drop(columns=["id_com"])

    center = pd.concat([center_com, center_arr])
    data = center.replace({np.nan: None})
    data["year_data"] = "2021"
    data["year_cog"] = "2021"
    return data


def load_commune_center(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_commune_center()

    cols_table = {
        "geo_code": "VARCHAR(50) NOT NULL",
        "centroid_lat": "FLOAT NULL DEFAULT NULL",
        "centroid_lon": "FLOAT NULL DEFAULT NULL",
        "chflieu_lat": "FLOAT NULL DEFAULT NULL",
        "chflieu_lon": "FLOAT NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NULL DEFAULT NULL",
        "year_cog": "VARCHAR(12) NULL DEFAULT NULL"
    }
    keys = "PRIMARY KEY (geo_code, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    print(get_commune_center())

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_commune_center(None, "ign_commune_center")

