"""Get the outline/boundary of commune"""

import polyline
import matplotlib.pyplot as plt
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection

from data_manager.ign.source import SOURCE_OUTLINE


def get_commune_outline(pool, geo_code):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT outline  
                FROM ign_commune_outline 
                WHERE (geo_code = ? AND source = ?)""", [geo_code, SOURCE_OUTLINE])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        commune_outline = [polyline.decode(o) for o in result[0].split(" ")]
        return commune_outline
    else:
        return None


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    outlines = get_commune_outline(None, "79048")
    for outline in outlines:
        print(outline)
        outline = np.array(outline)
        lats = outline[:, 0]
        lons = outline[:, 1]
        plt.plot(lons, lats)
        plt.axis("equal")
    plt.show()

