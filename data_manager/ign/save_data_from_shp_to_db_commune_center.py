"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import csv
import pandas as pd
import polyline
import shapefile
import json
import numpy as np
import matplotlib.pyplot as plt
import topojson as tp

from shapely.geometry import shape

from data_manager.database_connection.sql_connect import mariadb_connection


def read_shp_chef_lieu():
    sf = shapefile.Reader(
        "data/ADMIN-EXPRESS-COG-CARTO_3-1__SHP__FRA_WM_2022-04-15\ADMIN-EXPRESS-COG-CARTO/1_DONNEES_LIVRAISON_2022-04-15/ADECOGC_3-1_SHP_WGS84G_FRA/CHFLIEU_COMMUNE")

    chef_lieu_center = [r.__geo_interface__ for r in sf.shapeRecords()]
    chef_lieu = pd.DataFrame([{"id_com": c["properties"]["ID_COM"],
                               "chflieu_lat": c["geometry"]["coordinates"][1],
                               "chflieu_lon": c["geometry"]["coordinates"][0]}
                              for c in chef_lieu_center])
    print(chef_lieu)
    return chef_lieu


def read_shp_chef_lieu_arr():
    sf = shapefile.Reader(
        "data/ADMIN-EXPRESS-COG-CARTO_3-1__SHP__FRA_WM_2022-04-15\ADMIN-EXPRESS-COG-CARTO/1_DONNEES_LIVRAISON_2022-04-15/ADECOGC_3-1_SHP_WGS84G_FRA/CHFLIEU_ARR_MUN")

    chef_lieu_center = [r.__geo_interface__ for r in sf.shapeRecords()]
    chef_lieu = pd.DataFrame([{"id_com": c["properties"]["ID_COM"],
                               "chflieu_lat": c["geometry"]["coordinates"][1],
                               "chflieu_lon": c["geometry"]["coordinates"][0]}
                              for c in chef_lieu_center])
    print(chef_lieu)
    return chef_lieu


def read_shp_communes():
    sf = shapefile.Reader(
        "C:/Users/maelb/Documents/6 - Mobilite/1 - Produit/diagnostic-mobilite/data_manager/ign/data/ADMIN-EXPRESS-COG-CARTO_3-1__SHP__FRA_WM_2022-04-15/ADMIN-EXPRESS-COG-CARTO/1_DONNEES_LIVRAISON_2022-04-15\ADECOGC_3-1_SHP_WGS84G_FRA/COMMUNE")

    communes_geo = [r.__geo_interface__ for r in sf.shapeRecords()]
    communes = pd.DataFrame([{"id_com": c["properties"]["ID"],
                              "geo_code": c["properties"]["INSEE_COM"],
                              "centroid_lat": shape(c["geometry"]).centroid.y,
                              "centroid_lon": shape(c["geometry"]).centroid.x}
                             for c in communes_geo])
    print(communes)
    return communes


def read_shp_communes_arr():
    sf = shapefile.Reader(
        "C:/Users/maelb/Documents/6 - Mobilite/1 - Produit/diagnostic-mobilite/data_manager/ign/data/ADMIN-EXPRESS-COG-CARTO_3-1__SHP__FRA_WM_2022-04-15/ADMIN-EXPRESS-COG-CARTO/1_DONNEES_LIVRAISON_2022-04-15\ADECOGC_3-1_SHP_WGS84G_FRA/ARRONDISSEMENT_MUNICIPAL")

    communes_geo = [r.__geo_interface__ for r in sf.shapeRecords()]
    communes = pd.DataFrame([{"id_com": c["properties"]["ID"],
                              "geo_code": c["properties"]["INSEE_ARM"],
                              "centroid_lat": shape(c["geometry"]).centroid.y,
                              "centroid_lon": shape(c["geometry"]).centroid.x}
                             for c in communes_geo])
    print(communes)
    return communes


def save_commune_center_to_db(commune_center):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in commune_center.columns]) + ", source)"
    values_name = "(" + ", ".join(["?" for col in commune_center.columns]) + ", 'IGN_2022')"

    def request(cur, cols):
        cur.execute("""INSERT INTO ign_commune_center """ + cols_name + """ VALUES """ + values_name, cols)
    [request(cur, list(row.values)) for index, row in commune_center.iterrows()]

    conn.commit()
    conn.close()
    print("done")
    return

# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)
    # to prevent from unuseful loading data
    """
    chef_lieu = read_shp_chef_lieu()
    communes = read_shp_communes()
    commune_center = pd.merge(communes, chef_lieu, on="id_com", how="left").drop(columns=["id_com"])
    commune_center = commune_center.replace({np.nan: None})
    print(commune_center)"""

    communes_arr = read_shp_communes_arr()
    chef_lieu_arr = read_shp_chef_lieu_arr()
    commune_center_arr = pd.merge(communes_arr, chef_lieu_arr, on="id_com", how="left").drop(columns=["id_com"])
    commune_center_arr = commune_center_arr.replace({np.nan: None})
    print(commune_center_arr)
    security = True
    if not security:
        print(commune_center_arr[commune_center_arr["geo_code"] == "13201"])
        save_commune_center_to_db(commune_center_arr)
