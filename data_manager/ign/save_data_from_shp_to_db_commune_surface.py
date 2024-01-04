"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import os

import pandas as pd
import numpy as np
import shapefile
from pyproj import Transformer
from shapely import area
from shapely.ops import transform

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
    # Geodetic to Lambert coordinates system :
    transformer = Transformer.from_crs("epsg:4326",  # Système Inspire
                                       "epsg:2154")  # World Geodetic System (lat/lon)

    def geo_to_lambert(lon, lat):
        x, y = transformer.transform(lat, lon)
        return [x, y]

    def geojson_to_surface(geojson):
        geom_coll = GeometryCollection([shape(geojson["geometry"])])
        geom_coll_lambert = transform(geo_to_lambert, geom_coll)
        surface = round(area(geom_coll_lambert) / 1000000, 2)  # m² to km²
        return surface

    sf = shapefile.Reader(
        "data/2021/ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19/ADMIN-EXPRESS-COG/1_DONNEES_LIVRAISON_2021-05-19/ADECOG_3-0_SHP_WGS84G_FRA/COMMUNE")
    shapes = sf.shapeRecords()

    communes = pd.DataFrame([{
        "geo_code": s.__geo_interface__["properties"]["INSEE_COM"],
        "surface": geojson_to_surface(s.__geo_interface__),
        "year_data": "2021",
        "year_cog": "2021"
    } for s in shapes])

    communes = communes.replace({np.nan: None})

    return communes


def load_commune_surface(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = read_shp_outlines()

    cols_table = {
        "geo_code": "VARCHAR(50) NOT NULL",
        "surface": "FLOAT NULL DEFAULT NULL",
        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
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
        load_commune_surface(None, "ign_commune_surface")
