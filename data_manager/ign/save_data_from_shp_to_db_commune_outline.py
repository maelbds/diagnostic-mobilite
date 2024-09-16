import os
import shutil

import pandas as pd
import numpy as np
import shapefile
from shapely import wkb

from shapely.geometry import shape, GeometryCollection

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
    filter_func = lambda f: os.path.basename(f).split(".")[0] == "COMMUNE"

    return load_file_ign(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"], filter_func)


def get_commune_outline(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    # geometry to wkb
    def geojson_to_wkb_geometry_collection(geojson):
        geom_coll = GeometryCollection([shape(geojson["geometry"])])
        geom_wkb = wkb.dumps(geom_coll)
        return geom_wkb

    print("Reading shp communes")
    sf = shapefile.Reader(file_name.replace(".shp", ""))
    shapes = sf.shapeRecords()

    communes = pd.DataFrame([{
        "geo_code": s.__geo_interface__["properties"]["INSEE_COM"],
        "outline": geojson_to_wkb_geometry_collection(s.__geo_interface__),
        "year_cog": year_cog
    } for s in shapes])
    communes = communes.replace({np.nan: None})
    print(communes)

    return communes


"""
def shp_to_light_geojson():
    sf = shapefile.Reader(
        "data/ADMIN-EXPRESS-COG-CARTO_3-1__SHP__FRA_WM_2022-04-15\ADMIN-EXPRESS-COG-CARTO/1_DONNEES_LIVRAISON_2022-04-15\ADECOGC_3-1_SHP_WGS84G_FRA/COMMUNE")
    print('read')
    topo = tp.Topology(sf)
    print("topo done")
    topo.toposimplify(4).to_svg()

    return
"""


def load_commune_outline(pool):
    table_name = "ign_commune_outline"
    cols_table = {
        "geo_code": "VARCHAR(50) NOT NULL",
        "outline": "GEOMETRYCOLLECTION NULL DEFAULT NULL",

        "year_cog": "VARCHAR(12) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (geo_code, year_cog) USING BTREE"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_commune_outline(file_name, *missing_source)

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
        load_commune_outline(None)
