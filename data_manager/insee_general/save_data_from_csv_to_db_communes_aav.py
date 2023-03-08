import pandas as pd
import numpy as np
from pyproj import Transformer
import time

from data_manager.database_connection.sql_connect import mariadb_connection


def get_aav_from_csv():
    cols = ["CODGEO", "AAV2020", "CATEAAV2020"]
    print(cols)

    data = pd.read_csv(
        "data/aire_attraction_ville/liste_communes_aav.csv",
        sep=";", dtype=str,
        usecols=cols)
    data = data.rename(columns={"CODGEO": "geo_code", "AAV2020": "code_aav",
                                "CATEAAV2020": "cat_commune_aav"})
    print(data)
    return data


def save_aav_from_csv_to_db(aav):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in aav.columns]) + ", source)"
    values_name = "(" + ", ".join(["?" for col in aav.columns]) + ", 'AAV_2020')"

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_communes_aav """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in aav.iterrows()]

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
        aav = get_aav_from_csv()
        #save_aav_from_csv_to_db(aav)
