import os

import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.db_functions import load_database
from data_manager.utilities import load_file


def download_files():
    # reference : "https://www.insee.fr/fr/information/2510634"

    files = [{
        "name": "Base EPCI 2021",
        "url": "https://www.insee.fr/fr/statistiques/fichier/2510634/Intercommunalite_Metropole_au_01-01-2021.zip",
        "dir": "data/2021",
        "zip_name": "epci2021.zip",
        "file_name": "Intercommunalite-Metropole_au_01-01-2021.xlsx",
    },]

    [load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def load_data():
    """
    Read data from csv file & add it to the database
    :return:
    """
    epci_communes = ["CODGEO", "EPCI"]
    epci = ["EPCI", "LIBEPCI", "NATURE_EPCI", "NB_COM"]

    insee_epci_communes = pd.read_excel("data/2021/Intercommunalite-Metropole_au_01-01-2021.xlsx",
                                 sheet_name="Composition_communale", header=5, usecols=epci_communes, dtype="str")
    insee_epci = pd.read_excel("data/2021/Intercommunalite-Metropole_au_01-01-2021.xlsx",
                                 sheet_name="EPCI", header=5, usecols=epci, dtype="str")

    insee_epci["year_data"] = "2021"
    insee_epci["year_cog"] = "2021"

    insee_epci_communes["year_data"] = "2021"
    insee_epci_communes["year_cog"] = "2021"

    return insee_epci_communes, insee_epci


def save_data_insee_epci_communes(insee_epci_communes):
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in insee_epci_communes.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in insee_epci_communes.columns]) + ")"

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_epci_communes """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in insee_epci_communes.iterrows()]

    conn.commit()
    conn.close()


def save_data_insee_epci(insee_epci):
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in insee_epci.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in insee_epci.columns]) + ")"

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_epci """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in insee_epci.iterrows()]

    conn.commit()
    conn.close()


def load_epci(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    insee_epci_communes, insee_epci = load_data()

    data = insee_epci

    cols_table = {
        "EPCI": "VARCHAR(50) NOT NULL",
        "LIBEPCI": "VARCHAR(255) NULL DEFAULT NULL",
        "NATURE_EPCI": "VARCHAR(12) NULL DEFAULT NULL",
        "NB_COM": "INT(11) NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (EPCI, year_data) USING BTREE, KEY (LIBEPCI) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


def load_epci_communes(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    insee_epci_communes, insee_epci = load_data()

    data = insee_epci_communes

    cols_table = {
        "CODGEO": "VARCHAR(12) NOT NULL",
        "EPCI": "VARCHAR(12) NOT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (CODGEO, year_data) USING BTREE, KEY (EPCI) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)



# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.max_rows', 60)
    pd.set_option('display.width', 4000)

    download_files()

    insee_epci_communes, insee_epci = load_data()

    # to prevent from unuseful loading data
    security = True
    if not security:
        save_data_insee_epci(insee_epci)
        save_data_insee_epci_communes(insee_epci_communes)
