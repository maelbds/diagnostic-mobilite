"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import csv
import pandas as pd
import polyline
import shapefile
from pyproj import Transformer
import time
import json
import numpy as np
import matplotlib.pyplot as plt

from data_manager.database_connection.sql_connect import mariadb_connection


def read_shp_outlines():
    sf = shapefile.Reader("data/2017/grille200m_shp/grille200m_metropole_shp/grille200m_metropole")

    print(sf.fields)
    print(sf.shape(100).__geo_interface__)
    print(sf.shape(100).points)
    print(sf.record(100))
    #print(json.dumps(sf.shapeRecords()[100].__geo_interface__))

    # Lambert to Geodetic coordinates system :
    transformer = Transformer.from_crs("epsg:2154",  # Lambert 93
                                       "epsg:4326")  # World Geodetic System (lat/lon)
    def lambert_to_geo(x, y):
        lat, lon = transformer.transform(x, y)
        return lat, lon

    print()

    grids = []
    a = time.time()


    sf_len = len(sf)
    step = 100000

    for j in range(sf_len//step):
        print(f"{j * step} - {(j + 1) * step}")
        [grids.append({"idGrid200": sf.record(i)[0],
                      "outline": [(lambert_to_geo(x, y)) for x, y in sf.shape(i).points]})
         for i in range(j * step, (j+1) * step)]

    print(f"{sf_len//step * step} - {sf_len}")
    [grids.append({"idGrid200": sf.record(i)[0],
                   "outline": [(lambert_to_geo(x, y)) for x, y in sf.shape(i).points]})
     for i in range(sf_len//step * step, sf_len)]

    grids_df = pd.DataFrame(grids)
    print(grids_df)

    b = time.time()
    print(b-a)

    return grids_df


def save_outlines_to_db(outlines):
    conn = mariadb_connection()
    cur = conn.cursor()

    def request(cur, cols):
        cur.execute("""INSERT INTO ign_commune_outline 
                        (geo_code,
                        outline, 
                        source) VALUES (?,?,?)""", cols)

    [request(cur, [geo_code, " ".join([polyline.encode(o[0], geojson=True) for o in outline]), "IGN_2022"]) for geo_code, outline in
     zip(outlines["geo_code"], outlines["outline"])]

    conn.commit()
    conn.close()
    print("done")
    return



# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    # to prevent from unuseful loading data
    security = False
    if not security:
        pd.set_option('display.max_columns', 40)
        pd.set_option('display.max_rows', 100)
        pd.set_option('display.width', 1500)

        communes_outlines = read_shp_outlines()
        #save_outlines_to_db(communes_outlines)
