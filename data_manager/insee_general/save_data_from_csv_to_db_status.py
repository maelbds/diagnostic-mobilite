import pandas as pd
import numpy as np
from pyproj import Transformer
import time

from data_manager.database_connection.sql_connect import mariadb_connection


def get_status_from_csv():
    cols = ["CODGEO", "STATUT_2017"]
    print(cols)

    data = pd.read_csv(
        "data/statut/statut_communes_2021.csv",
        sep=";", dtype=str,
        usecols=cols)
    data = data.rename(columns={"CODGEO": "geo_code", "STATUT_2017": "status_code"})
    print(data)
    return data


def save_status_from_csv_to_db(status):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in status.columns]) + ", source)"
    values_name = "(" + ", ".join(["?" for col in status.columns]) + ", 'UU_2020')"

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_communes_status """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in status.iterrows()]

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
        status = get_status_from_csv()
        #save_status_from_csv_to_db(status)
