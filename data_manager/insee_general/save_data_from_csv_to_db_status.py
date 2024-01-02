import os

import pandas as pd

from data_manager.db_functions import load_database
from data_manager.utilities import load_file


def download_files():
    # reference : "https://www.insee.fr/fr/information/4802589"

    files = [{
        "name": "Base des unités urbaines 2020 - COG 2021",
        "url": "https://www.insee.fr/fr/statistiques/fichier/4802589/UU2020_au_01-01-2021.zip",
        "dir": "data/2021",
        "zip_name": "base_uu_2021.zip",
        "file_name": "UU2020_au_01-01-2021.xlsx",
    },]

    [load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def get_status_from_csv():
    cols = ["CODGEO", "STATUT_2017"]
    data = pd.read_excel("data/2021/UU2020_au_01-01-2021.xlsx",
                         sheet_name="Composition_communale", usecols=cols, header=5, dtype="str")

    data = data.rename(columns={"CODGEO": "geo_code", "STATUT_2017": "status_code"})
    data["year_data"] = "2020"
    data["year_cog"] = "2021"
    return data


def load_status(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_status_from_csv()

    cols_table = {
        "geo_code": "VARCHAR(12) NOT NULL",
        "status_code": "VARCHAR(2) NULL DEFAULT NULL",
        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (geo_code, year_data, year_cog) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


def load_status_types(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    data = pd.DataFrame(
                [
                    {
                        "type_code": "B",
                        "type_name": "Banlieue",
                        "year_data": "2020"
                    },
                    {
                        "type_code": "C",
                        "type_name": "Ville-centre",
                        "year_data": "2020"
                    },
                    {
                        "type_code": "H",
                        "type_name": "Hors unité urbaine",
                        "year_data": "2020"
                    },
                    {
                        "type_code": "I",
                        "type_name": "Ville isolée",
                        "year_data": "2020"
                    }
                ]
    )

    cols_table = {
        "type_code": "VARCHAR(50) NOT NULL",
        "type_name": "VARCHAR(50) NULL DEFAULT NULL",
        "year_data": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (type_code, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    download_files()
    print(get_status_from_csv())

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_status(None, "insee_communes_status")
        load_status_types(None, "insee_communes_status_types")
