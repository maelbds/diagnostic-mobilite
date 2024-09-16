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
        "zip_name": f"densite{year_cog}.zip",
        "file_name": f"grille_densite_{year_cog}_detaille.xlsx",
    }

    return load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"])


def get_density_from_csv(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    cols = {"\nCode \nCommune\n": "geo_code", "Typo degré de \nDensité\n": "density_code"}
    data = pd.read_excel(file_name, sheet_name="grille_com_dens_fr_Entiere_4NIV",
                         header=0, dtype="str", usecols=cols.keys())

    data = data.rename(columns=cols)
    data = data.replace({np.nan: None})
    data["year_data"] = year_data
    data["year_cog"] = year_cog
    return data


def load_density(pool):
    table_name = "insee_communes_density"
    cols_table = {
        "geo_code": "VARCHAR(12) NOT NULL",
        "density_code": "VARCHAR(2) NULL DEFAULT NULL",
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
        data = get_density_from_csv(file_name, *missing_source)

        load_database(pool, table_name, data, cols_table, keys)

        os.remove(file_name)
        save_source(pool, *missing_source)


def load_density_types(pool):
    table_name = "insee_communes_density_types"
    data = pd.DataFrame(
        [
            {
                "type_code": "1",
                "type_name": "Commune densément peuplée",
                "year_data": "2020"
            },
            {
                "type_code": "2",
                "type_name": "Commune de densité intermédiaire",
                "year_data": "2020"
            },
            {
                "type_code": "3",
                "type_name": "Commune peu dense",
                "year_data": "2020"
            },
            {
                "type_code": "4",
                "type_name": "Commune très peu dense",
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
        load_density(None)
        load_density_types(None)
