"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import csv
import pandas as pd
import polyline
import shapefile
import json

from data_manager.database_connection.sql_connect import mariadb_connection


def read_shp_outlines():
    sf = shapefile.Reader("data/2022/communes-20220101-shp/communes-20220101")

    communes_geo = [r.__geo_interface__ for r in sf.shapeRecords()]

    communes_outlines = pd.DataFrame([{"geo_code": c["properties"]["insee"],
                              "outline": [c["geometry"]["coordinates"]]} if c["geometry"]["type"] == "Polygon" else
                             {"geo_code": c["properties"]["insee"],
                              "outline": c["geometry"]["coordinates"]}
                             for c in communes_geo])
    print(communes_outlines)
    print(communes_outlines[communes_outlines["geo_code"] == "29042"])
    return communes_outlines



def save_outlines_to_db(outlines):
    conn = mariadb_connection()
    cur = conn.cursor()

    def request(cur, cols):
        cur.execute("""INSERT INTO osm_commune_outline 
                    (geo_code,
                        outline, 
                        date, source) VALUES (?,?,CURRENT_TIMESTAMP,?)""", cols)

    [request(cur, [geo_code, " ".join([polyline.encode(o[0], geojson=True) for o in outline]), "OSM_2022"]) for geo_code, outline in
     zip(outlines["geo_code"], outlines["outline"])]

    conn.commit()
    conn.close()
    print("done")
    return



# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    # to prevent from unuseful loading data
    security = True
    if not security:
        pd.set_option('display.max_columns', 40)
        pd.set_option('display.max_rows', 100)
        pd.set_option('display.width', 1500)

        communes_outlines = read_shp_outlines()
        #save_outlines_to_db(communes_outlines)
