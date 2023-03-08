import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely import wkb

import pyproj
from shapely.ops import transform

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.transportdatagouv.source import SOURCE_ZFE


def get_zfe(pool, geo_codes):
    def wkb_to_geojson(wkb_geom):
        geom_collection = wkb.loads(wkb_geom)
        geom = geom_collection[0].__geo_interface__
        return geom

    conn = mariadb_connection(pool)
    cur = conn.cursor()

    geo_codes = [g[:5] for g in geo_codes]
    geo_codes_str = ",".join(geo_codes)

    cur.execute("""SELECT id, date_debut, date_fin, vp_critair, vp_horaires, geometry
                FROM transportdatagouv_zfe
                WHERE main_geo_code IN (""" + geo_codes_str + """) AND source = ? 
                AND (date_fin > NOW() OR ISNULL(date_fin))""", [SOURCE_ZFE])
    result = list(cur)
    conn.close()

    zfe = pd.DataFrame(result, columns=["id", "date_debut", "date_fin",
                                                "vp_critair", "vp_horaires",
                                                "geometry"])
    zfe["geometry"] = [wkb_to_geojson(r) for r in zfe["geometry"]]
    zfe["date_debut"] = zfe["date_debut"].astype(str)
    zfe["date_fin"] = zfe["date_fin"].astype(str)

    return zfe


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)

    zfe = get_zfe(None, ["51454"])
    print(zfe)

