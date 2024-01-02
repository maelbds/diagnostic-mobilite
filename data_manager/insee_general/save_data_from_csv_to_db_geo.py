import pandas as pd
import numpy as np
import os

from data_manager.db_functions import load_database
from data_manager.utilities import load_file


def download_files():
    # reference : "https://www.insee.fr/fr/information/2028028"

    files = [{
        "name": "Géographie communes 2021",
        "url": "https://www.insee.fr/fr/statistiques/fichier/2028028/table-appartenance-geo-communes-21.zip",
        "dir": "data/2021",
        "zip_name": "commune_geo2021.zip",
        "file_name": "table-appartenance-geo-communes-21.xlsx",
    }]

    [load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def get_geo_communes_from_csv():
    cols = ["CODGEO", "LIBGEO", "DEP", "REG", "EPCI", "ARR", "CV"]
    data = pd.read_excel(
        "data/2021/table-appartenance-geo-communes-21.xlsx", sheet_name="COM",
        header=5, dtype=str,
        usecols=cols)

    data = data.replace({np.nan: None})
    data["year_data"] = "2021"
    data["year_cog"] = "2021"
    return data


def load_geo_communes(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_geo_communes_from_csv()

    cols_table = {
        "CODGEO": "VARCHAR(12) NOT NULL",
        "LIBGEO": "VARCHAR(255) NULL DEFAULT NULL",
        "CV": "VARCHAR(12) NULL DEFAULT NULL",
        "EPCI": "VARCHAR(12) NULL DEFAULT NULL",
        "ARR": "VARCHAR(12) NULL DEFAULT NULL",
        "DEP": "VARCHAR(12) NULL DEFAULT NULL",
        "REG": "VARCHAR(12) NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (CODGEO, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = False
    if not security:
        load_geo_communes(None, "insee_geo_communes")
