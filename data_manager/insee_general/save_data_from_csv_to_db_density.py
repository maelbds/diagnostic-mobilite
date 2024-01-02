import os

import pandas as pd

from data_manager.db_functions import load_database
from data_manager.utilities import load_file


def download_files():
    # reference : "https://www.insee.fr/fr/information/2114627"

    files = [{
        "name": "Densité communes 2020 - COG 2021",
        "url": "https://www.insee.fr/fr/statistiques/fichier/2114627/grille_densite_2021.zip",
        "dir": "data/2021",
        "zip_name": "densite2021.zip",
        "file_name": "grille_densite_2021_detaille.xlsx",
    },]

    [load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def get_density_from_csv():
    cols = {"\nCode \nCommune\n": "geo_code", "Typo degré de \nDensité\n": "density_code"}

    data = pd.read_excel("data/2021/grille_densite_2021_detaille.xlsx", sheet_name="grille_com_dens_fr_Entiere_4NIV",
                         header=0, dtype="str", usecols=cols.keys())

    data = data.rename(columns=cols)
    data["year_data"] = "2020"
    data["year_cog"] = "2021"
    return data


def load_density(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_density_from_csv()

    cols_table = {
        "geo_code": "VARCHAR(12) NOT NULL",
        "density_code": "VARCHAR(2) NULL DEFAULT NULL",
        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (geo_code, year_data, year_cog) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


def load_density_types(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    data = pd.DataFrame(
                [
                    {
                        "type_code": "1",
                        "type_name": "communes densément peuplées",
                        "year_data": "2020"
                    },
                    {
                        "type_code": "2",
                        "type_name": "communes de densité intermédiaire",
                        "year_data": "2020"
                    },
                    {
                        "type_code": "3",
                        "type_name": "communes peu denses",
                        "year_data": "2020"
                    },
                    {
                        "type_code": "4",
                        "type_name": "communes très peu denses",
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

    density = get_density_from_csv()
    print(density)

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_density(None, "insee_communes_density")
        load_density_types(None, "insee_communes_density_types")
