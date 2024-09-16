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
        "dir": f"data/{year_cog}",
        "zip_name": f"{name}_{year_cog}.zip",
        "file_name": f"table_passage_geo2003_geo{year_cog}.xlsx",
    }

    return load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"])


def get_passage_cog(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    cols = {"CODGEO_INI": "CODGEO_INI", f"CODGEO_{year_cog}": "CODGEO_DES"}

    data = pd.read_excel(file_name, sheet_name="Table de passage", header=5, dtype="str", usecols=cols.keys())
    data = data.rename(columns=cols)

    data = data.replace({np.nan: None})
    data["year_cog"] = year_cog
    return data


def load_passage_cog(pool):
    table_name = "insee_passage_cog"
    cols_table = {
        "CODGEO_INI": "VARCHAR(12) NOT NULL",
        "CODGEO_DES": "VARCHAR(12) NULL DEFAULT NULL",

        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (CODGEO_INI, year_cog) USING BTREE, KEY (CODGEO_INI) USING BTREE, KEY (CODGEO_DES) USING BTREE"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_passage_cog(file_name, *missing_source)

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
        load_passage_cog(None)
