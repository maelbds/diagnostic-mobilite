"""Get the outline/boundary of commune"""
import os

import matplotlib.pyplot as plt
import numpy as np
from shapely import wkb
import shapefile
import pandas as pd
from shapely.geometry import shape

from data_manager.database_connection.sql_connect import mariadb_connection

from data_manager.ign.source import SOURCE_OUTLINE


def get_commune_outline(pool, geo_code):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT outline  
                FROM ign_commune_outline 
                WHERE (geo_code = ? AND year_cog = ?)""", [geo_code, SOURCE_OUTLINE])
    result = list(cur)
    conn.close()

    def wkb_to_geojson(wkb_geom):
        geom_collection = wkb.loads(wkb_geom)
        geom = geom_collection[0].__geo_interface__
        return geom

    if len(result) > 0:
        result = result[0]
        commune_outline = [wkb_to_geojson(r) for r in result]
        return commune_outline
    else:
        return None


def get_all_commune_outline_shapely(pool):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT geo_code, outline  
                FROM ign_commune_outline 
                WHERE year_cog = ?""", [SOURCE_OUTLINE])
    result = list(cur)
    conn.close()

    def wkb_to_shapely(wkb_geom):
        return wkb.loads(wkb_geom)

    communes_outlines = pd.DataFrame(result, columns=["geo_code", "outline"])
    communes_outlines["outline"] = [wkb_to_shapely(outline) for outline in communes_outlines["outline"]]

    return communes_outlines


def read_shp_outlines_communes():
    print("Reading data communes")
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    sf = shapefile.Reader(
        "data/ADMIN-EXPRESS-COG-CARTO_3-1__SHP__FRA_WM_2022-04-15/ADMIN-EXPRESS-COG-CARTO/1_DONNEES_LIVRAISON_2022-04-15/ADECOGC_3-1_SHP_WGS84G_FRA/COMMUNE")

    shapes = sf.shapes()
    records = sf.records()

    communes = pd.DataFrame([{
        "geo_code": r["INSEE_COM"],
        "outline": shape(s.__geo_interface__),
    } for s, r in zip(shapes, records)])
    return communes


# ---------------------------------------------------------------------------------


if __name__ == '__main__':
    print(get_all_commune_outline_shapely(None))