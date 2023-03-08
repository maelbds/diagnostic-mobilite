import pandas as pd
import numpy as np
from pyproj import Transformer
import time

from data_manager.database_connection.sql_connect import mariadb_connection


def get_adjacent_from_csv():
    cols = ["insee", "insee_voisins"]
    data = pd.read_csv(
        "data/2022/communes_adjacentes_2022.csv",
        sep=",", dtype=str,
        usecols=cols)
    data = data.rename(columns={"insee": "geo_code", "insee_voisins": "geo_code_neighbor"})
    data["geo_code_neighbor"] = data["geo_code_neighbor"].apply(lambda x: x.split("|"))
    data = data.explode("geo_code_neighbor").drop_duplicates()
    return data


def save_adjacent_from_csv_to_db(data):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ", source)"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ", 'OSM_2022')"

    def request(cur, cols):
        cur.execute("""INSERT INTO osm_adjacent """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    adjacent = get_adjacent_from_csv()
    print(adjacent)


    # to prevent from unuseful loading data
    security = False
    if not security:
        save_adjacent_from_csv_to_db(adjacent)
