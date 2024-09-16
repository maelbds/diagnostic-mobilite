import os

import pandas as pd
import numpy as np

from data_manager.db_functions import load_database
from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.utilities import load_file

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


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    filename = f"Intercommunalite-Metropole_au_01-01-{year_cog}.xlsx" if year_cog == "2021" \
        else f"Intercommunalite_Metropole_au_01-01-{year_cog}.xlsx"

    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_cog}",
        "zip_name": f"{id}.zip",
        "file_name": filename,
    }

    return load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"])


def get_epci_from_csv(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    cols = ["EPCI", "LIBEPCI", "NATURE_EPCI", "NB_COM"]
    data = pd.read_excel(file_name, sheet_name="EPCI", header=5, usecols=cols, dtype="str")

    data = data.replace({np.nan: None})
    data["year_cog"] = year_cog
    return data


def load_epci(pool):
    table_name = "insee_epci"
    cols_table = {
        "EPCI": "VARCHAR(50) NOT NULL",
        "LIBEPCI": "VARCHAR(255) NULL DEFAULT NULL",
        "NATURE_EPCI": "VARCHAR(12) NULL DEFAULT NULL",
        "NB_COM": "INT(11) NULL DEFAULT NULL",

        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (EPCI, year_cog) USING BTREE, KEY (LIBEPCI) USING BTREE"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_epci_from_csv(file_name, *missing_source)

        load_database(pool, table_name, data, cols_table, keys)

        os.remove(file_name)
        save_source(pool, *missing_source)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.max_rows', 60)
    pd.set_option('display.width', 4000)

    # to prevent from unuseful loading data
    security = False
    if not security:
        load_epci(None)
