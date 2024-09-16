"""Get the outline/boundary of epci"""

import polyline
import matplotlib.pyplot as plt
import numpy as np
from shapely import wkb

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.ign.source import SOURCE_OUTLINE


def get_epci_outline(epci_siren):
    conn = mariadb_connection()
    cur = conn.cursor()
    cur.execute("""SELECT outline  
                FROM ign_epci_outline 
                WHERE (epci_siren = ? AND year_data = ?)""", [epci_siren, SOURCE_OUTLINE])
    result = list(cur)
    conn.close()

    def wkb_to_geojson(wkb_geom):
        geom_collection = wkb.loads(wkb_geom)
        geom = geom_collection[0].__geo_interface__
        return geom

    if len(result) > 0:
        result = result[0]
        epci_outline = [wkb_to_geojson(r) for r in result]
        return epci_outline
    else:
        return None


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    def plot_geojson(shapes, color=None):
        for s in shapes:
            if s["type"] == "Polygon":
                outline = np.array(s["coordinates"][0])
                lats = outline[:, 0]
                lons = outline[:, 1]
                if color is not None:
                    plt.plot(lats, lons, color)
                else:
                    plt.plot(lats, lons)
            elif s["type"] == "MultiPolygon":
                for p in s["coordinates"]:
                    outline = np.array(p[0])
                    lats = outline[:, 0]
                    lons = outline[:, 1]
                    if color is not None:
                        plt.plot(lats, lons, color)
                    else:
                        plt.plot(lats, lons)

    outlines = get_epci_outline("200066868")
    plot_geojson(outlines)
    plt.axis("equal")
    plt.show()

