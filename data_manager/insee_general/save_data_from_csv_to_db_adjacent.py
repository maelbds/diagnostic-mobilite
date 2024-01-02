import os
import numpy as np
import pandas as pd

from data_manager.db_functions import load_database
from data_manager.utilities import download_url


def download_files():
    # reference : "https://www.data.gouv.fr/fr/datasets/liste-des-adjacences-des-communes-francaises/"

    file = {
        "name": "OSM adjacent communes 2021",
        "url": "http://osm13.openstreetmap.fr/~cquest/openfla/communes_adjacentes_2021.csv",
        "dir": "data/2021",
        "file_name": "communes_adjacentes_2021.csv",
    }

    download_url(file["url"], f"{file['dir']}/{file['file_name']}")



def get_adjacent_from_csv():
    cols = ["insee", "insee_voisins"]
    data = pd.read_csv(
        #"data/2022/communes_adjacentes_2022.csv",
        "data/2021/communes_adjacentes_2021.csv",
        sep=",", dtype=str,
        usecols=cols)

    data = data.rename(columns={"insee": "geo_code", "insee_voisins": "geo_code_neighbor"})
    data["geo_code_neighbor"] = data["geo_code_neighbor"].apply(lambda x: x.split("|"))
    data = data.explode("geo_code_neighbor").drop_duplicates()

    data["year_data"] = "2021"
    data["year_cog"] = "2021"
    data = data.replace({np.nan: None})
    return data


def load_adjacent(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    data = get_adjacent_from_csv()

    cols_table = {
        "geo_code": "VARCHAR(12) NOT NULL",
        "geo_code_neighbor": "VARCHAR(12) NOT NULL",
        "source": "VARCHAR(20) NOT NULL",
    }
    keys = "PRIMARY KEY (geo_code, geo_code_neighbor) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


def load_adjacent(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_adjacent_from_csv()

    cols_table = {
        "geo_code": "VARCHAR(12) NOT NULL",
        "geo_code_neighbor": "VARCHAR(12) NOT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (geo_code, geo_code_neighbor, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 70)
    pd.set_option('display.width', 2000)

    download_files()
    adjacent = get_adjacent_from_csv()
    print(adjacent)

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_adjacent(None, "osm_adjacent")

