import os

import pandas as pd
import numpy as np
from pyproj import Transformer
import time

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.db_functions import load_database


def get_cog_from_csv():
    cols = ["MOD", "DATE_EFF", "COM_AV", "TYPECOM_AV", "COM_AP", "TYPECOM_AP"]
    print(cols)

    data = pd.read_csv(
        "data/2022/mvtcommune_2022.csv",
        sep=",", dtype=str,
        usecols=cols)
    print(data)
    data["COG"] = 2022
    data["id"] = data.index.values
    data.rename(columns={"MOD": "MODA"}, inplace=True)
    return data


def save_cog_to_db(cog):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ",".join([col for col in cog.columns]) + ")"
    values_name = "(" + ",".join(["?" for col in cog.columns]) + ")"

    print(cols_name)
    print(values_name)

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_cog_evenements """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in cog.iterrows()]

    conn.commit()
    conn.close()


def load_cog_evenements(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    data = get_cog_from_csv()

    cols_table = {
        "id": "INT(11) NOT NULL",
        "MODA": "VARCHAR(12) NOT NULL",
        "DATE_EFF": "DATE NOT NULL",
        "TYPECOM_AV": "VARCHAR(12) NOT NULL",
        "COM_AV": "VARCHAR(12) NOT NULL",
        "TYPECOM_AP": "VARCHAR(12) NOT NULL",
        "COM_AP": "VARCHAR(12) NOT NULL",
        "COG": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (id) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)



# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    cog = get_cog_from_csv()
    print(cog)

    # to prevent from unuseful loading data
    security = True
    if not security:
        save_cog_to_db(cog)
