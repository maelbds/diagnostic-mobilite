"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import os
import numpy as np
import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.db_functions import load_database
from data_manager.utilities import load_file_gridded_pop


def download_files():
    # reference : "https://www.insee.fr/fr/statistiques/6215138?sommaire=6215217#consulter"

    files = [{
        "name": "INSEE Filosofi Données au carreau 200m 2017",
        "url": "https://www.insee.fr/fr/statistiques/fichier/6215138/Filosofi2017_carreaux_200m_csv.zip",
        "dir": "data/2017",
        "zip_name": "filosofi2017.zip",
        "zip_name2": "Filosofi2017_carreaux_200m_csv.7z",
        "file_name": "Filosofi2017_carreaux_200m_met.csv",
    }]

    [load_file_gridded_pop(f["name"], f["url"], f["dir"], f["zip_name"], f["zip_name2"], f["file_name"]) for f in files]


def read_gridded_pop_csv():
    useful_cols = ["Idcar_200m", "lcog_geo", "Ind", "Men", "Men_pauv", "Men_prop", "Ind_snv", "Men_surf"]
    g_pop = pd.read_csv("data/2017/Filosofi2017_carreaux_200m_met.csv", sep=",",
                        dtype="str", usecols=useful_cols)
    g_pop = g_pop.rename(columns={"Idcar_200m": "idGrid200", "lcog_geo": "geo_code"})
    g_pop = g_pop.astype({"Ind": "float", "Men": "float",
                          "Men_pauv": "float", "Men_prop": "float",
                          "Ind_snv": "float", "Men_surf": "float"})
    g_pop["geo_code"] = g_pop["geo_code"].apply(lambda x: x[:5])

    g_pop["year_data"] = "2017"
    g_pop["year_cog"] = "2021"
    g_pop = g_pop.replace({np.nan: None})

    print(g_pop)
    return g_pop


def load_gridded_pop(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = read_gridded_pop_csv()

    cols_table = {
        "idGrid200": "VARCHAR(50) NOT NULL",
        "Ind": "FLOAT NULL DEFAULT NULL",
        "Men": "FLOAT NULL DEFAULT NULL",
        "Men_pauv": "FLOAT NULL DEFAULT NULL",
        "Men_prop": "FLOAT NULL DEFAULT NULL",
        "Ind_snv": "FLOAT NULL DEFAULT NULL",
        "Men_surf": "FLOAT NULL DEFAULT NULL",
        "geo_code": "VARCHAR(50) NULL DEFAULT NULL",

        "year_data": "VARCHAR(20) NOT NULL",
        "year_cog": "VARCHAR(20) NOT NULL",
    }
    keys = "PRIMARY KEY (idGrid200, year_data) USING BTREE, KEY (geo_code) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    # to prevent from unuseful loading data
    security = False
    if not security:
        load_gridded_pop(None, "insee_filosofi_gridded_pop")
