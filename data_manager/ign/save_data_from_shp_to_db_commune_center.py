"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import os
import shutil

import pandas as pd
import shapefile
import numpy as np

from shapely.geometry import shape

from data_manager.db_functions import load_database
from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.utilities import load_file_ign


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_cog}/{id}",
        "zip_name": f"{id}.7z",
        "file_name": "COMMUNE.shp",
    }
    filter_func = lambda f: os.path.basename(f).split(".")[0] in \
                            ["CHFLIEU_COMMUNE", "COMMUNE",
                             "CHFLIEU_ARRONDISSEMENT_MUNICIPAL", "ARRONDISSEMENT_MUNICIPAL"]

    return load_file_ign(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"], filter_func)


def read_shp_chef_lieu_com(filename, year_cog):
    sf = shapefile.Reader(filename)
    chef_lieu_center = [r.__geo_interface__ for r in sf.shapeRecords()]
    chef_lieu = pd.DataFrame([{"id_com": c["properties"]["ID_COM"],
                               "chflieu_lat": c["geometry"]["coordinates"][1],
                               "chflieu_lon": c["geometry"]["coordinates"][0]}
                              for c in chef_lieu_center])
    return chef_lieu


def read_shp_chef_lieu_arr(filename, year_cog):
    sf = shapefile.Reader(filename)
    chef_lieu_center = [r.__geo_interface__ for r in sf.shapeRecords()]
    chef_lieu = pd.DataFrame([{"id_com": c["properties"]["ID_COM"] if year_cog == "2021" else c["properties"]["ID_ARM"],
                               "chflieu_lat": c["geometry"]["coordinates"][1],
                               "chflieu_lon": c["geometry"]["coordinates"][0]}
                              for c in chef_lieu_center])
    return chef_lieu


def read_shp_centroid_com(filename, year_cog):
    sf = shapefile.Reader(filename)
    communes_geo = [r.__geo_interface__ for r in sf.shapeRecords()]
    communes = pd.DataFrame([{"id_com": c["properties"]["ID"],
                              "geo_code": c["properties"]["INSEE_COM"],
                              "centroid_lat": shape(c["geometry"]).centroid.y,
                              "centroid_lon": shape(c["geometry"]).centroid.x}
                             for c in communes_geo])
    return communes


def read_shp_centroid_arr(filename, year_cog):
    sf = shapefile.Reader(filename)
    communes_geo = [r.__geo_interface__ for r in sf.shapeRecords()]
    communes = pd.DataFrame([{"id_com": c["properties"]["ID"],
                              "geo_code": c["properties"]["INSEE_ARM"],
                              "centroid_lat": shape(c["geometry"]).centroid.y,
                              "centroid_lon": shape(c["geometry"]).centroid.x}
                             for c in communes_geo])
    return communes


def get_commune_center(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    chef_lieu_com = read_shp_chef_lieu_com(f"data/{year_cog}/{id}/CHFLIEU_COMMUNE", year_cog)
    chef_lieu_arr = read_shp_chef_lieu_arr(f"data/{year_cog}/{id}/CHFLIEU_ARRONDISSEMENT_MUNICIPAL", year_cog)
    centroid_com = read_shp_centroid_com(f"data/{year_cog}/{id}/COMMUNE", year_cog)
    centroid_arr = read_shp_centroid_arr(f"data/{year_cog}/{id}/ARRONDISSEMENT_MUNICIPAL", year_cog)

    center_com = pd.merge(centroid_arr, chef_lieu_arr, on="id_com", how="left").drop(columns=["id_com"])
    center_arr = pd.merge(centroid_com, chef_lieu_com, on="id_com", how="left").drop(columns=["id_com"])

    center = pd.concat([center_com, center_arr])
    data = center.replace({np.nan: None})
    data["year_cog"] = year_cog
    print(data)
    return data


def load_commune_center(pool):
    table_name = "ign_commune_center"
    cols_table = {
        "geo_code": "VARCHAR(50) NOT NULL",
        "centroid_lat": "FLOAT NULL DEFAULT NULL",
        "centroid_lon": "FLOAT NULL DEFAULT NULL",
        "chflieu_lat": "FLOAT NULL DEFAULT NULL",
        "chflieu_lon": "FLOAT NULL DEFAULT NULL",

        "year_cog": "VARCHAR(12) NULL DEFAULT NULL"
    }
    keys = "PRIMARY KEY (geo_code, year_cog) USING BTREE"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_commune_center(file_name, *missing_source)

        load_database(pool, table_name, data, cols_table, keys)

        shutil.rmtree(f"data/{year_cog}/{id}")
        save_source(pool, *missing_source)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    # to prevent from unuseful loading data
    security = False
    if not security:
        load_commune_center(None)

