import numpy as np
import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.transportdatagouv.source import SOURCE_BNLC


def get_bnlc(pool, geo_code):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT id_lieu, nom_lieu, type, insee, Ylat, Xlong, nbre_pl, nbre_pmr, date_maj
                FROM transportdatagouv_bnlc 
                WHERE (insee = ? AND source = ?)""", [geo_code, SOURCE_BNLC])
    result = list(cur)
    conn.close()

    bnlc = pd.DataFrame(result, columns=["id", "name", "type", "geo_code", "lat", "lon",
                                                "nbre_pl", "nbre_pmr", "date_maj"])

    bnlc["nbre_pl"] = bnlc["nbre_pl"].replace({np.nan: None})
    bnlc["nbre_pmr"] = bnlc["nbre_pmr"].replace({np.nan: None})
    bnlc["date_maj"] = bnlc["date_maj"].astype(str)
    return bnlc


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)

    bnlc = get_bnlc(None, "59380")
    print(bnlc)
