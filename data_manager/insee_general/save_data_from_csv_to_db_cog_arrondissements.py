import pandas as pd
import numpy as np
import os

from data_manager.db_functions import load_database
from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.utilities import load_file, download_url


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    if year_cog == "2021":
        f = {
            "name": id,
            "url": link,
            "dir": f"data/{year_cog}",
            "zip_name": f"arrondissement{year_cog}.zip",
            "file_name": f"arrondissement{year_cog}.csv",
        }

    elif year_cog == "2023":
        f = {
            "name": id,
            "url": link,
            "dir": f"data/{year_cog}",
            "zip_name": None,
            "file_name": f"v_arrondissement_{year_cog}.csv",
        }

    return load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"])


def get_cog_arrondissements_from_csv(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    cols = ["ARR", "DEP", "REG", "CHEFLIEU", "NCCENR", "LIBELLE"]
    data = pd.read_csv(file_name, sep=",", dtype=str, usecols=cols)

    data = data.replace({np.nan: None})
    data["year_cog"] = year_cog
    return data


def load_cog_arrondissements(pool):
    table_name = "insee_cog_arrondissements"
    cols_table = {
        "ARR": "VARCHAR(12) NOT NULL",
        "NCCENR": "VARCHAR(255) NULL DEFAULT NULL",
        "LIBELLE": "VARCHAR(255) NULL DEFAULT NULL",
        "DEP": "VARCHAR(12) NULL DEFAULT NULL",
        "REG": "VARCHAR(12) NULL DEFAULT NULL",
        "CHEFLIEU": "VARCHAR(12) NULL DEFAULT NULL",

        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (ARR, year_cog) USING BTREE"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_cog_arrondissements_from_csv(file_name, *missing_source)

        load_database(pool, table_name, data, cols_table, keys)

        os.remove(file_name)
        save_source(pool, *missing_source)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = False
    if not security:
        load_cog_arrondissements(None)
