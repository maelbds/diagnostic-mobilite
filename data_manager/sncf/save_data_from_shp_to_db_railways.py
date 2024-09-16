"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import os
import shutil
import numpy as np

import pandas as pd
import shapefile
from shapely import wkb, prepare, crosses
from shapely.ops import unary_union

from shapely.geometry import shape, GeometryCollection

# geometry to wkb
from data_manager.ign.commune_outline import get_all_commune_outline_shapely

from data_manager.db_functions import load_database
from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.utilities import load_file


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_cog}/{id}",
        "zip_name": f"{id}.zip",
        "file_name": "lignes-par-region-administrative.shp",
    }

    return load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"])


def shape_to_wkb_geometry_collection(shape):
    geom_coll = GeometryCollection([shape])
    geom_wkb = wkb.dumps(geom_coll)
    return geom_wkb


def read_shp_outlines_railways(file_name):
    print("Reading data railways")
    sf = shapefile.Reader(file_name.replace(".shp", ""))

    records = sf.records()

    railways = pd.DataFrame([{
        "idgaia": s["idgaia"],
        "code_ligne": s["code_ligne"],
        "lib_ligne": s["lib_ligne"],
        "region": s["region"],
        "rg_troncon": s["rg_troncon"]
    } for s in records])

    shapes = sf.shapes()
    railways["geometry_shape_WGS"] = [shape(s.__geo_interface__) for s in shapes]
    railways.drop_duplicates(subset="idgaia", inplace=True)

    return railways


def get_railways(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    railways = read_shp_outlines_railways(file_name)

    railways["geometry"] = [shape_to_wkb_geometry_collection(r) for r in railways["geometry_shape_WGS"]]
    railways.drop(columns=["geometry_shape_WGS"], inplace=True)
    railways["year_data"] = "2023"
    print("railways :")
    print(railways)

    return railways


def get_railways_communes(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    railways = read_shp_outlines_railways(file_name)
    communes = get_all_commune_outline_shapely(None)

    [prepare(s) for s in communes["outline"]]

    def agg_func(df):
        return pd.Series({
            "geometry": unary_union(df["geometry_shape_WGS"])
        })
    railways_s = railways.groupby("lib_ligne", as_index=False).apply(agg_func)
    print("railways grouped by line")

    communes["railways"] = [[r_name for r_name, r_shape
                           in zip(railways_s["lib_ligne"], railways_s["geometry"])
                           if crosses(c, r_shape)]
                          for c in communes["outline"]]
    print("railways by commune found")

    communes_railways = []
    [communes_railways.append(pd.DataFrame({
        "CODGEO": [geo_code for r in railways],
        "lib_ligne": [r for r in railways],
    })) for geo_code, railways in zip(communes["geo_code"], communes["railways"])]
    communes_railways = pd.concat(communes_railways)

    communes_railways["year_data"] = year_data
    communes_railways["year_cog"] = year_cog
    print("railways communes :")
    print(communes_railways)

    return communes_railways


def load_railways(pool):
    table_name = "sncf_railways"
    cols_table = {
        "idgaia": "VARCHAR(50) NOT NULL",
        "code_ligne": "VARCHAR(50) NOT NULL",
        "lib_ligne": "VARCHAR(200) NULL DEFAULT NULL",
        "region": "VARCHAR(50) NULL DEFAULT NULL",
        "rg_troncon": "VARCHAR(50) NULL DEFAULT NULL",
        "geometry": "GEOMETRYCOLLECTION NULL DEFAULT NULL",

        "year_data": "VARCHAR(20) NOT NULL",
    }
    keys = "PRIMARY KEY (idgaia, year_data) USING BTREE, KEY (lib_ligne) USING BTREE"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)

        data = get_railways(file_name, *missing_source)

        load_database(pool, table_name, data, cols_table, keys)

        shutil.rmtree(f"data/{year_cog}/{id}")
        save_source(pool, *missing_source)


def load_railways_communes(pool):
    table_name = "sncf_railways_communes"
    cols_table = {
        "CODGEO": "VARCHAR(50) NOT NULL",
        "lib_ligne": "VARCHAR(200) NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (CODGEO, lib_ligne, year_data) USING BTREE, KEY (CODGEO) USING BTREE"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)

        data = get_railways_communes(file_name, *missing_source)

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
        load_railways(None)
        load_railways_communes(None)
