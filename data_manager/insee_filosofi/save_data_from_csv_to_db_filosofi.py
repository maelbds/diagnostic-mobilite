import pandas as pd
import numpy as np
import os

from data_manager.db_functions import load_database
from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.utilities import load_file


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    mesh = name.replace("insee_filosofi_", "").upper()
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_data}",
        "zip_name": f"{name}_{year_data}.zip",
        "file_name": f"FILO{year_data}_DISP_{mesh}.csv",
    }

    return load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"])


def get_data_from_csv(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    variables = pd.read_csv("data/variables_filosofi.csv", sep=";", dtype=str)
    cols = variables["variables"].dropna().drop_duplicates().tolist()
    cols = {(f"{col}{year_data[2:]}" if col != "RD" and col != "CODGEO" else col): col for col in cols}

    data = pd.read_csv(file_name, sep=";", dtype=str, usecols=cols.keys())
    data = data.rename(columns=cols)

    data["mesh"] = name.replace("insee_filosofi_", "").upper()
    data["year_data"] = year_data
    data["year_cog"] = year_cog

    data = data.replace({np.nan: None})

    return data


def load_filosofi(pool):
    table_name = "insee_filosofi"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_data_from_csv(file_name, *missing_source)

        cols_table = {
            "CODGEO": "VARCHAR(12) NOT NULL",

            "Q1": "INT(11) NULL DEFAULT NULL",
            "Q2": "INT(11) NULL DEFAULT NULL",
            "Q3": "INT(11) NULL DEFAULT NULL",
            "RD": "FLOAT NULL DEFAULT NULL",
            "S80S20": "FLOAT NULL DEFAULT NULL",
            "GI": "FLOAT NULL DEFAULT NULL",

            "mesh": "VARCHAR(12) NOT NULL",
            "year_data": "VARCHAR(12) NOT NULL",
            "year_cog": "VARCHAR(12) NOT NULL",
        }
        keys = "PRIMARY KEY (CODGEO, mesh, year_data) USING BTREE"

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
        load_filosofi(None)
