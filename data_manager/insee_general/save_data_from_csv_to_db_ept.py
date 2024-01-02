import os

import pandas as pd

from data_manager.db_functions import load_database
from data_manager.utilities import download_url
from openpyxl.styles.colors import WHITE, RGB


# patch to fix xls problem reading with pandas : ValueError: Colors must be aRGB hex values pandas read excel
__old_rgb_set__ = RGB.__set__


def __rgb_set_fixed__(self, instance, value):
    try:
        __old_rgb_set__(self, instance, value)
    except ValueError as e:
        if e.args[0] == 'Colors must be aRGB hex values':
            __old_rgb_set__(self, instance, WHITE)  # Change default color here


RGB.__set__ = __rgb_set_fixed__
# end of patch


def download_files():
    # reference : "https://www.insee.fr/fr/information/2510634"

    file = {
        "name": "Base EPT 2023",
        "url": "https://www.insee.fr/fr/statistiques/fichier/2510634/ept_au_01-01-2023.xlsx",
        "dir": "data/2023",
        "file_name": "ept_au_01-01-2023.xlsx",
    }

    download_url(file["url"], f"{file['dir']}/{file['file_name']}")


def load_data():
    """
    Read data from csv file & add it to the database
    :return:
    """
    ept_communes = ["CODGEO", "EPT"]
    ept = ["EPT", "LIBEPT", "NB_COM"]

    insee_ept_communes = pd.read_excel("data/2023/ept_au_01-01-2023.xlsx", sheet_name="Composition_communale",
                                       header=5, usecols=ept_communes, dtype="str")
    insee_ept = pd.read_excel("data/2023/ept_au_01-01-2023.xlsx", sheet_name="EPT",
                              header=5, usecols=ept, dtype="str")

    insee_ept["year_data"] = "2023"
    insee_ept["year_cog"] = "2023"

    insee_ept_communes["year_data"] = "2023"
    insee_ept_communes["year_cog"] = "2023"

    return insee_ept_communes, insee_ept


def load_ept(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    insee_ept_communes, insee_ept = load_data()

    data = insee_ept

    cols_table = {
        "EPT": "VARCHAR(50) NOT NULL",
        "LIBEPT": "VARCHAR(255) NULL DEFAULT NULL",
        "NB_COM": "INT(11) NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (EPT, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


def load_ept_communes(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    insee_ept_communes, insee_ept = load_data()

    data = insee_ept_communes

    cols_table = {
        "CODGEO": "VARCHAR(12) NOT NULL",
        "EPT": "VARCHAR(12) NOT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (CODGEO, year_data) USING BTREE, KEY (EPT) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.max_rows', 60)
    pd.set_option('display.width', 4000)

    download_files()

    insee_ept_communes, insee_ept = load_data()

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_ept(None, "insee_ept")
        load_ept_communes(None, "insee_ept_communes")
