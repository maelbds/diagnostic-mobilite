import pandas as pd
import numpy as np
import os

from data_manager.db_functions import load_database
from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.utilities import load_file


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_data}",
        "zip_name": f"{name}_{year_data}.zip",
        "file_name": f"indicateur_precarite_tee.csv",
    }

    return load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"])


def get_data_from_csv(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    cols = ["zone", "carburant", "carburant_pourcentage", "logement_carburant", "logement_carburant_pourcentage"]
    data = pd.read_csv(file_name, sep=";", decimal=",", usecols=cols)

    data["geo_code"] = data["zone"].apply(lambda x: x.split("(")[-1].split(")")[0])
    data = data.drop(columns=["zone"])

    data["year_data"] = year_data
    data["year_cog"] = year_cog

    data = data.replace({np.nan: None})

    return data


def load_geodip(pool):
    table_name = "geodip_precariousness"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_data_from_csv(file_name, *missing_source)

        cols_table = {
            "geo_code": "VARCHAR(12) NOT NULL",

            "carburant": "INT(11) NULL DEFAULT NULL",
            "logement_carburant": "INT(11) NULL DEFAULT NULL",
            "carburant_pourcentage": "FLOAT NULL DEFAULT NULL",
            "logement_carburant_pourcentage": "FLOAT NULL DEFAULT NULL",

            "year_data": "VARCHAR(12) NOT NULL",
            "year_cog": "VARCHAR(12) NOT NULL",
        }
        keys = "PRIMARY KEY (geo_code, year_data) USING BTREE"

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
        load_geodip(None)

