"""Get the outline/boundary of commune"""

import pprint
import polyline
import matplotlib.pyplot as plt
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.osm.api_request import api_osm_request_commune_outline
from data_manager.osm.functions_format import process_osm_data_outline

from data_manager.osm.source import SOURCE_OUTLINE


def get_commune_outline_api(geo_code):
    commune_outline = process_osm_data_outline(api_osm_request_commune_outline(geo_code))
    return commune_outline


def get_commune_outline_bdd(geo_code):
    conn = mariadb_connection()
    cur = conn.cursor()
    cur.execute("""SELECT outline  
                FROM osm_commune_outline 
                WHERE (geo_code = ? AND source = ?)""", [geo_code, SOURCE_OUTLINE])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        commune_outline = [polyline.decode(o) for o in result[0].split(" ")]
        return commune_outline
    else:
        return None


def save_commune_outline_bdd(geo_code):
    commune_outline = get_commune_outline_api(geo_code)

    conn = mariadb_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO osm_commune_outline 
                    (geo_code,
                        outline, 
                        date) VALUES (?,?,CURRENT_TIMESTAMP)""",
                [geo_code,
                 " ".join([polyline.encode(o) for o in commune_outline])]
                )

    conn.commit()
    conn.close()
    print("Outline for commune " + str(geo_code) + " saved")
    return commune_outline


def get_commune_outline(geo_code):
    commune_outline = get_commune_outline_bdd(geo_code)
    if commune_outline is None:
        commune_outline = save_commune_outline_bdd(geo_code)
    return commune_outline


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    outlines = get_commune_outline(29042)
    for outline in outlines:
        print(outline)
        outline = np.array(outline)
        lats = outline[:, 0]
        lons = outline[:, 1]
        plt.plot(lons, lats)
        plt.axis("equal")
    plt.show()

