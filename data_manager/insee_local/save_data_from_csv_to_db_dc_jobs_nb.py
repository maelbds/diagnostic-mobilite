import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection


def get_jobs_nb_from_csv():
    cols = ["CODGEO", "P18_EMPLT"]
    data = pd.read_csv(
        "data/2018/dossier_complet/dossier_complet.csv",
        sep=";", dtype=str, usecols=cols)
    data = data.rename(columns={"CODGEO": "geo_code", "P18_EMPLT": "jobs_nb"})
    data = data.dropna()
    data = data.astype({"jobs_nb": "float"})
    data["jobs_nb"] = data["jobs_nb"].round()
    return data


def save_jobs_nb_bdd(data):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_jobs_nb 
                    (geo_code, 
                    jobs_nb, 
                    date,
                    source) VALUES (?,?,CURRENT_TIMESTAMP, ?)""", cols)

    [request(cur, [geo_code, jobs_nb, "INSEE_RP_2018"])
     for geo_code, jobs_nb in
     zip(data["geo_code"], data["jobs_nb"])]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = True
    if not security:
        data = get_jobs_nb_from_csv()
