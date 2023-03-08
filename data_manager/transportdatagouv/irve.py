import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.transportdatagouv.source import SOURCE_IRVE


def get_irve(pool, geo_codes):
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    def get_irve_by_geo_code(geo_code):
        cur.execute("""SELECT id, id_station_itinerance, nom_station, code_insee_commune, lat, lon, nbre_pdc, puissance_nominale, date_maj
                    FROM transportdatagouv_irve 
                    WHERE (code_insee_commune = ? AND source = ?)""", [geo_code, SOURCE_IRVE])
        result = list(cur)

        irve = pd.DataFrame(result, columns=["id", "id_station", "nom_station", "geo_code", "lat", "lon",
                                                    "nbre_pdc", "puissance_nominale", "date_maj"])
        return irve

    all_irve = pd.concat([get_irve_by_geo_code(g) for g in geo_codes])
    conn.close()

    all_irve["nbre_pdc"] = all_irve["nbre_pdc"].replace({np.nan: None})
    all_irve["date_maj"] = all_irve["date_maj"].astype(str)

    all_irve.drop_duplicates(subset=["nom_station", "geo_code", "lat", "lon",
                                     "nbre_pdc", "puissance_nominale", "date_maj"],
                             inplace=True)
    return all_irve


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)

    irve = get_irve(None, ["13055", "13201"])
    print(irve)
