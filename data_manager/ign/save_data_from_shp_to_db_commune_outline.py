"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import os

import pandas as pd
import numpy as np
import shapefile
from shapely import wkb

from shapely.geometry import shape, GeometryCollection

from data_manager.db_functions import load_database
from data_manager.utilities import load_file_ign


def download_files():
    # reference : "https://geoservices.ign.fr/adminexpress"

    files = [{
        "name": "ADMIN-EXPRESS-COG édition 2021 France entière",
        "url": "https://wxs.ign.fr/x02uy2aiwjo9bm8ce5plwqmr/telechargement/prepackage/ADMINEXPRESS-COG_SHP_WGS84G_PACK_2021-05-19$ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19/file/ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19.7z",
        "dir": "data/2021",
        "zip_name": "ign_admin_express_2021.zip",
        "file_name": "ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19/ADMIN-EXPRESS-COG/1_DONNEES_LIVRAISON_2021-05-19/ADECOG_3-0_SHP_WGS84G_FRA/COMMUNE.shp",
    }]

    [load_file_ign(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def read_shp_outlines():
    # geometry to wkb
    def geojson_to_wkb_geometry_collection(geojson):
        geom_coll = GeometryCollection([shape(geojson["geometry"])])
        geom_wkb = wkb.dumps(geom_coll)
        return geom_wkb

    sf = shapefile.Reader(
        "data/2021/ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19/ADMIN-EXPRESS-COG/1_DONNEES_LIVRAISON_2021-05-19/ADECOG_3-0_SHP_WGS84G_FRA/COMMUNE")
    shapes = sf.shapeRecords()

    communes = pd.DataFrame([{
        "geo_code": s.__geo_interface__["properties"]["INSEE_COM"],
        "outline": geojson_to_wkb_geometry_collection(s.__geo_interface__),
        "year_data": "2021",
        "year_cog": "2021"
    } for s in shapes])
    communes = communes.replace({np.nan: None})

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


def load_commune_outline(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = read_shp_outlines()

    cols_table = {
        "geo_code": "VARCHAR(50) NOT NULL",
        "outline": "GEOMETRYCOLLECTION NULL DEFAULT NULL",
        "year_data": "VARCHAR(12) NULL DEFAULT NULL",
        "year_cog": "VARCHAR(12) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (geo_code, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    communes_outlines = read_shp_outlines()

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_commune_outline(None, "ign_commune_outline")
