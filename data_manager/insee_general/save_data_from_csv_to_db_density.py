import pandas as pd
import numpy as np
from pyproj import Transformer
import time

from data_manager.database_connection.sql_connect import mariadb_connection


def get_density_from_csv():
    cols = ["geo_code", "code_densite"]

    data = pd.read_csv(
        "data/2022/grille_densite_niveau_detaille_2022.csv",
        sep=";", dtype=str,
        usecols=cols)
    data = data.rename(columns={"geo_code": "geo_code", "code_densite": "density_code"})
    data["source"] = "density_2020"
    print(data)
    return data


def save_density_from_csv_to_db(status):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in status.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in status.columns]) + ")"

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_communes_density """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in status.iterrows()]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    density = get_density_from_csv()

    # to prevent from unuseful loading data
    security = True
    if not security:
        save_density_from_csv_to_db(density)
