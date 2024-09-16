import pandas as pd
import numpy as np
from shapely import geometry, wkb
import matplotlib.pyplot as plt

from data_manager.database_connection.sql_connect import mariadb_connection


def get_emd_geo(pool, emd_id):
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    cur.execute("""SELECT 
                   id, name, geo_code, geo_code_city, geometry
                   FROM emd_geo
                   LEFT JOIN insee_arrondissements ON geo_code=geo_code_district
                   WHERE emd_id = ? """, [emd_id])
    result = list(cur)
    conn.close()

    zones = pd.DataFrame(result, columns=["id", "name", "geo_code", "geo_code_city", "geometry"])

    def wkb_to_geojson(wkb_geom):
        geom_collection = wkb.loads(wkb_geom)
        geom = geom_collection[0].__geo_interface__
        return geom

    def geo_to_center(geo):
        geom = geometry.shape(geo)
        return geom.representative_point().coords[0]

    zones["geometry"] = zones["geometry"].apply(lambda geo: wkb_to_geojson(geo))
    zones["center"] = zones["geometry"].apply(lambda geo: geo_to_center(geo))

    marseille_mask = zones["geo_code_city"] == "13055"
    zones.loc[marseille_mask, "name"] = "Marseille"
    zones.loc[marseille_mask, "geo_code"] = "13055"
    zones.loc[marseille_mask, "center"] = zones.loc[marseille_mask, "center"].apply(lambda x: (43.2955, 5.3697))

    lyon_mask = zones["geo_code_city"] == "69123"
    zones.loc[lyon_mask, "name"] = "Lyon"
    zones.loc[lyon_mask, "geo_code"] = "69123"
    zones.loc[lyon_mask, "center"] = zones.loc[lyon_mask, "center"].apply(lambda x: (45.764, 4.8356))

    return zones


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    emd_geo = get_emd_geo(None, "lyon")
    print(emd_geo)
    print(emd_geo.drop(columns=["geometry"]).drop_duplicates(subset="geo_code").set_index("geo_code"))

    for z, c in zip(emd_geo["geometry"], emd_geo["center"]):
        """for polygon in z["coordinates"]:
            outline = np.array(polygon[0])
            lats = outline[:, 0]
            lons = outline[:, 1]
            plt.plot(lons, lats)"""
        plt.plot(c[1], c[0], "r+")
    plt.axis("equal")
    plt.show()



