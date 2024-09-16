import os

import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.db_functions import load_database


def load_data():
    """
    Read data from csv file & add it to the database
    :return:
    """
    cols = {"#Code_commune_INSEE": "CODGEO",
            "Nom_de_la_commune": "LIBELLE",
            "Code_postal": "code_postal",
            "Libellé_d_acheminement": "libelle_acheminement",
            "Ligne_5": "ligne_5"}
    data = pd.read_csv("data/base_code_postal.csv", usecols=cols.keys(), dtype="str", encoding="latin-1", sep=";")

    data = data.rename(columns=cols)

    data["year_data"] = "2023"
    data["id"] = data.index.values
    data = data.replace({np.nan: None})

    return data


def save_data(data, database_name):
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ")"

    def request(cur, cols):
        cur.execute("""INSERT INTO  """ + database_name + " " + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

    conn.commit()
    conn.close()


def load_code_postal(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    data = load_data()

    cols_table = {
        "id": "INT(11) NOT NULL",
        "CODGEO": "VARCHAR(12) NULL DEFAULT NULL",
        "LIBELLE": "VARCHAR(100) NULL DEFAULT NULL",
        "code_postal": "VARCHAR(12) NULL DEFAULT NULL",
        "libelle_acheminement": "VARCHAR(200) NULL DEFAULT NULL",
        "ligne_5": "VARCHAR(200) NULL DEFAULT NULL",

        "year_data": "VARCHAR(50) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (id) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)



# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.max_rows', 60)
    pd.set_option('display.width', 4000)

    data = load_data()

    # to prevent from unuseful loading data
    security = True
    if not security:
        save_data(data, "la_poste_code_postal")
