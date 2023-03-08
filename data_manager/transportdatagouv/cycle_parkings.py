import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely import wkb

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.transportdatagouv.source import SOURCE_CYCLE_PARKINGS


def get_cycle_parkings(pool, geo_code):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT id, code_com, lat, lon, capacite, gestionnaire, date_maj
                FROM transportdatagouv_cycle_parkings 
                WHERE (code_com = ? AND source = ?)""", [geo_code, SOURCE_CYCLE_PARKINGS])
    result = list(cur)
    conn.close()

    cycle_parkings = pd.DataFrame(result, columns=["id", "code_com", "lat", "lon",
                                                "capacite", "gestionnaire", "date_maj"])

    cycle_parkings["capacite"] = cycle_parkings["capacite"].replace({np.nan: None})
    cycle_parkings["date_maj"] = cycle_parkings["date_maj"].astype(str)
    return cycle_parkings


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)

    cycle_parkings = get_cycle_parkings(None, "13001")
    print(cycle_parkings)
