"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import csv
import pprint

import pandas as pd
import polyline
import shapefile
import json
import numpy as np
import matplotlib.pyplot as plt
import topojson as tp

from shapely.geometry import shape, Polygon, MultiPolygon, GeometryCollection
from shapely import wkb

from data_manager.ign.simplify_outline import simplify_outline

from data_manager.database_connection.sql_connect import mariadb_connection


def read_shp_outlines():
    # geometry to wkb
    def geojson_to_wkb_geometry_collection(geojson):
        geom_coll = GeometryCollection([shape(geojson["geometry"])])
        geom_wkb = wkb.dumps(geom_coll)
        return geom_wkb

    print("Reading data")
    sf = shapefile.Reader(
        "data/ADMIN-EXPRESS-COG-CARTO_3-1__SHP__FRA_WM_2022-04-15\ADMIN-EXPRESS-COG-CARTO/1_DONNEES_LIVRAISON_2022-04-15\ADECOGC_3-1_SHP_WGS84G_FRA/EPCI")
    shapes = sf.shapeRecords()

    epci_geo = {"type": "FeatureCollection", "features": [s.__geo_interface__ for s in shapes]}
    print(epci_geo)
    with open('total_epci_geo.json', 'w') as outfile:
        json.dump(epci_geo, outfile)

    # geojson shapes
    outlines = [s.__geo_interface__ for s in shapes]
    light_outlines = simplify_outline(outlines, 0.003)

    epci = pd.DataFrame({"epci_siren": [o["properties"]["CODE_SIREN"] for o in outlines]})
    epci["outline"] = [geojson_to_wkb_geometry_collection(o) for o in outlines]
    epci["outline_light"] = [geojson_to_wkb_geometry_collection(o) for o in light_outlines]
    epci["source"] = "IGN 2022"
    print(epci)

    return epci


def save_data_to_db(outlines):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in outlines.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in outlines.columns]) + ")"

    def request(cur, cols):
        cur.execute("""INSERT INTO ign_epci_outline """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in outlines.iterrows()]

    conn.commit()
    conn.close()




# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    epci_outlines = read_shp_outlines()

    # to prevent from unuseful loading data
    security = True
    if not security:
        save_data_to_db(epci_outlines)
