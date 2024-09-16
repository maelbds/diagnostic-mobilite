import os
import numpy as np
import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.db_functions import load_database

from data_manager.db_functions import load_database
from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.util_districts import get_districts_to_city_dict
from data_manager.utilities import load_file_gridded_pop


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_data}",
        "zip_name": f"{name}_{year_data}.zip",
        "zip_name2": f"Filosofi{year_data}_carreaux_200m_csv.7z",
        "file_name": f"Filosofi{year_data}_carreaux_200m_met.csv" if year_data == "2017" else "carreaux_200m_met.csv",
    }

    return load_file_gridded_pop(f["name"], f["url"], f["dir"], f["zip_name"], f["zip_name2"], f["file_name"])


def get_data_from_csv(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    useful_cols = ["idcar_200m", "lcog_geo", "ind", "men", "men_pauv", "men_prop", "ind_snv", "men_surf"]
    data = pd.read_csv(file_name, sep=",",dtype="str", usecols=lambda x: x.lower() in useful_cols)
    data1 = pd.read_csv(file_name.replace("met", "mart"), sep=",", dtype="str", usecols=lambda x: x.lower() in useful_cols)
    data2 = pd.read_csv(file_name.replace("met", "reun"), sep=",", dtype="str", usecols=lambda x: x.lower() in useful_cols)
    data = pd.concat([data, data1, data2])

    data = data.rename(columns=lambda x: x.lower())
    data = data.rename(columns={"idcar_200m": "idGrid200", "lcog_geo": "geo_code"})
    data = data.astype({"ind": "float", "men": "float", "geo_code": "string",
                          "men_pauv": "float", "men_prop": "float",
                          "ind_snv": "float", "men_surf": "float"})
    data = data.dropna(subset=["geo_code"])
    data["geo_code"] = data["geo_code"].apply(lambda x: x[:5])
    data["geo_code"] = data["geo_code"].replace(to_replace=get_districts_to_city_dict())

    data["year_data"] = year_data
    data["year_cog"] = year_cog
    data = data.replace({np.nan: None})

    return data


def load_gridded_pop(pool):
    table_name = "insee_filosofi_gridded_pop"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_data_from_csv(file_name, *missing_source)

        cols_table = {
            "idGrid200": "VARCHAR(50) NOT NULL",
            "ind": "FLOAT NULL DEFAULT NULL",
            "men": "FLOAT NULL DEFAULT NULL",
            "men_pauv": "FLOAT NULL DEFAULT NULL",
            "men_prop": "FLOAT NULL DEFAULT NULL",
            "ind_snv": "FLOAT NULL DEFAULT NULL",
            "men_surf": "FLOAT NULL DEFAULT NULL",
            "geo_code": "VARCHAR(50) NULL DEFAULT NULL",

            "year_data": "VARCHAR(20) NOT NULL",
            "year_cog": "VARCHAR(20) NOT NULL",
        }
        keys = "PRIMARY KEY (idGrid200, year_data) USING BTREE, KEY (geo_code) USING BTREE"

        load_database(pool, table_name, data, cols_table, keys)

        os.remove(file_name)
        os.remove(file_name.replace("met", "mart"))
        os.remove(file_name.replace("met", "reun"))
        save_source(pool, *missing_source)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    # to prevent from unuseful loading data
    security = False
    if not security:
        load_gridded_pop(None)
