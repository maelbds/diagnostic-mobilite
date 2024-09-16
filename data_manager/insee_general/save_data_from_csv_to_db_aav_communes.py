import pandas as pd
import numpy as np
import os

from data_manager.db_functions import load_database
from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.utilities import load_file, download_url
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
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_cog}",
        "zip_name": f"AAV2020_au_01-01-{year_cog}.zip",
        "file_name": f"AAV2020_au_01-01-{year_cog}.xlsx",
    }

    return load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"])


def get_aav_communes_from_csv(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    cols = ["CODGEO", "AAV2020", "CATEAAV2020"]
    data = pd.read_excel(file_name, sheet_name="Composition_communale", header=5, usecols=cols, dtype="str")

    data.rename(columns={n: n.replace("2020", "").replace("2017", "") for n in data.columns}, inplace=True)
    data = data.replace({np.nan: None})
    data["year_data"] = year_data
    data["year_cog"] = year_cog
    return data


def load_aav_communes(pool):
    table_name = "insee_aav_communes"
    cols_table = {
        "CODGEO": "VARCHAR(12) NOT NULL",
        "AAV": "VARCHAR(12) NULL DEFAULT NULL",
        "CATEAAV": "VARCHAR(12) NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (CODGEO, year_data, year_cog) USING BTREE"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_aav_communes_from_csv(file_name, *missing_source)

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
        load_aav_communes(None)