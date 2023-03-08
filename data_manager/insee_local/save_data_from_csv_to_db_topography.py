import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection


def get_topography_from_csv():
    cols_1 = ["Code", "Libellé", "Superficie 2018"]
    surface = pd.read_csv(
        "data/2018/superficie_2018.csv",
        sep=";", dtype=str, skiprows=2,
        usecols=cols_1)
    surface = surface.rename(columns={"Code": "geo_code", "Superficie 2018": "surface"})
    surface = surface.dropna()

    cols_2 = ["Code", "Densité de population (historique depuis 1876) 2018", "Taux d'artificialisation des sols, 2018"]
    artificialization = pd.read_csv(
        "data/2018/densite-taux_artificialisation_sols_2018.csv",
        sep=";", dtype=str, skiprows=2,
        usecols=cols_2)
    artificialization = artificialization.rename(columns={"Code": "geo_code",
                                      "Densité de population (historique depuis 1876) 2018": "density",
                                      "Taux d'artificialisation des sols, 2018": "artificialization_rate"})
    artificialization = artificialization.dropna()

    topo = pd.merge(surface, artificialization, on="geo_code", how="left")
    topo = topo.replace({np.nan: None})
    print(topo)
    return topo


def save_topography_bdd(data):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_topography 
                    (geo_code, 
                    surface, 
                    density, 
                    artificialization_rate,
                    date,
                    source) VALUES (?,?,?,?,CURRENT_TIMESTAMP, ?)""", cols)

    [request(cur, [geo_code, surface, density, artificialization_rate, "INSEE_RP_2018"])
     for geo_code, surface, density, artificialization_rate in
     zip(data["geo_code"], data["surface"], data["density"], data["artificialization_rate"])]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = False
    if not security:
        data = get_topography_from_csv()



