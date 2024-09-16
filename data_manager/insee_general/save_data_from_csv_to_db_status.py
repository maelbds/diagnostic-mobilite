import os

import pandas as pd
import numpy as np

from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.utilities import load_file
from data_manager.db_functions import create_new_table, empty_table, load_table, load_database


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_cog}",
        "zip_name": f"base_uu_{year_cog}.zip",
        "file_name": f"UU2020_au_01-01-{year_cog}.xlsx",
    }

    return load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"])


def get_status_from_csv(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    cols = {"CODGEO": "geo_code", "STATUT_2017": "status_code"}
    data = pd.read_excel(file_name, sheet_name="Composition_communale", usecols=cols.keys(), header=5, dtype="str")

    data = data.rename(columns=cols)
    data = data.replace({np.nan: None})
    data["year_data"] = year_data
    data["year_cog"] = year_cog
    return data


def load_status(pool):
    table_name = "insee_communes_status"
    cols_table = {
        "geo_code": "VARCHAR(12) NOT NULL",
        "status_code": "VARCHAR(2) NULL DEFAULT NULL",
        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (geo_code, year_data, year_cog) USING BTREE"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_status_from_csv(file_name, *missing_source)

        load_database(pool, table_name, data, cols_table, keys)

        os.remove(file_name)
        save_source(pool, *missing_source)


def load_status_types(pool):
    table_name = "insee_communes_status_types"
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

    create_new_table(pool, table_name, cols_table, keys)
    empty_table(pool, table_name)
    load_table(pool, table_name, data, cols_table)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = False
    if not security:
        load_status(None)
        load_status_types(None)
