import pandas as pd
import numpy as np
import os

from data_manager.db_functions import load_database
from data_manager.utilities import load_file


def download_files():
    # reference : "https://www.insee.fr/fr/information/5057840"

    files = [{
        "name": "COG communes 2021",
        "url": "https://www.insee.fr/fr/statistiques/fichier/5057840/commune2021-csv.zip",
        "dir": "data/2021",
        "zip_name": "commune2021.zip",
        "file_name": "commune2021.csv",
    }, {
        "name": "COG arrondissements 2021",
        "url": "https://www.insee.fr/fr/statistiques/fichier/5057840/arrondissement2021-csv.zip",
        "dir": "data/2021",
        "zip_name": "arrondissement2021.zip",
        "file_name": "arrondissement2021.csv",
    }, {
        "name": "COG departements 2021",
        "url": "https://www.insee.fr/fr/statistiques/fichier/5057840/departement2021-csv.zip",
        "dir": "data/2021",
        "zip_name": "departement2021.zip",
        "file_name": "departement2021.csv",
    }]

    [load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def get_cog_communes_from_csv():
    cols = ["TYPECOM", "COM", "DEP", "REG", "CAN", "ARR", "NCCENR", "LIBELLE", "COMPARENT"]
    data = pd.read_csv(
        "data/2021/commune2021.csv",
        sep=",", dtype=str,
        usecols=cols)

    data = data[(data["TYPECOM"] == "COM") | (data["TYPECOM"] == "ARM")]  # to remove former communes
    data.drop(columns=["TYPECOM"], inplace=True)

    data = data.replace({np.nan: None})
    data["year_data"] = "2021"
    data["year_cog"] = "2021"
    return data


def get_cog_arrondissements_from_csv():
    cols = ["ARR", "DEP", "REG", "CHEFLIEU", "NCCENR", "LIBELLE"]
    data = pd.read_csv(
        "data/2021/arrondissement2021.csv",
        sep=",", dtype=str,
        usecols=cols)

    data = data.replace({np.nan: None})
    data["year_data"] = "2021"
    data["year_cog"] = "2021"
    return data


def get_cog_departements_from_csv():
    cols = ["DEP", "REG", "CHEFLIEU", "NCCENR", "LIBELLE"]
    data = pd.read_csv(
        "data/2021/departement2021.csv",
        sep=",", dtype=str,
        usecols=cols)

    data = data.replace({np.nan: None})
    data["year_data"] = "2021"
    data["year_cog"] = "2021"
    return data


def load_cog_communes(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_cog_communes_from_csv()

    cols_table = {
        "COM": "VARCHAR(12) NOT NULL",
        "NCCENR": "VARCHAR(255) NULL DEFAULT NULL",
        "LIBELLE": "VARCHAR(255) NULL DEFAULT NULL",
        "CAN": "VARCHAR(12) NULL DEFAULT NULL",
        "ARR": "VARCHAR(12) NULL DEFAULT NULL",
        "DEP": "VARCHAR(12) NULL DEFAULT NULL",
        "REG": "VARCHAR(12) NULL DEFAULT NULL",
        "COMPARENT": "VARCHAR(12) NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (COM, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


def load_cog_arrondissements(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_cog_arrondissements_from_csv()

    cols_table = {
        "ARR": "VARCHAR(12) NOT NULL",
        "NCCENR": "VARCHAR(255) NULL DEFAULT NULL",
        "LIBELLE": "VARCHAR(255) NULL DEFAULT NULL",
        "DEP": "VARCHAR(12) NULL DEFAULT NULL",
        "REG": "VARCHAR(12) NULL DEFAULT NULL",
        "CHEFLIEU": "VARCHAR(12) NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (ARR, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


def load_cog_departements(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_cog_departements_from_csv()

    cols_table = {
        "DEP": "VARCHAR(12) NOT NULL",
        "NCCENR": "VARCHAR(255) NULL DEFAULT NULL",
        "LIBELLE": "VARCHAR(255) NULL DEFAULT NULL",
        "REG": "VARCHAR(12) NULL DEFAULT NULL",
        "CHEFLIEU": "VARCHAR(12) NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (DEP, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    download_files()
    exit()

    cog_communes = get_cog_communes_from_csv()
    print(cog_communes)

    cog_arrondissements = get_cog_arrondissements_from_csv()
    cog_arrondissements["year_data"] = "2022"
    cog_arrondissements["year_cog"] = "2022"
    print(cog_arrondissements)

    cog_departements = get_cog_departements_from_csv()
    cog_departements["year_data"] = "2022"
    cog_departements["year_cog"] = "2022"
    print(cog_departements)

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_cog_communes(None, "insee_cog_communes")
