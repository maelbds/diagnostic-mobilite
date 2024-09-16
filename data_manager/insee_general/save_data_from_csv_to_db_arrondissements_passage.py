import pandas as pd
import numpy as np
import os

from data_manager.db_functions import load_database
from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.utilities import load_file, download_url


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_cog}",
        "zip_name": None,
        "file_name": f"v_commune_depuis_1943.csv",
    }

    return load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"])


def get_cog_communes_from_csv(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    cols = ["COM"]
    data = pd.read_csv(file_name, sep=",", dtype=str, usecols=cols)

    data = data.rename(columns={"COM": "geo_code_city"})
    data["geo_code_district"] = data["geo_code_city"]

    marseille_districts = ["13201", "13202", "13203", "13204", "13205", "13206", "13207", "13208",
                           "13209", "13210", "13211", "13212", "13213", "13214", "13215", "13216"]
    marseille_city = "13055"
    marseille = pd.DataFrame(data={
        "geo_code_district": marseille_districts,
        "geo_code_city": [marseille_city for i in marseille_districts]
    })

    lyon_districts = ["69381", "69382", "69383", "69384", "69385", "69386", "69387", "69388", "69389"]
    lyon_city = "69123"
    lyon = pd.DataFrame(data={
        "geo_code_district": lyon_districts,
        "geo_code_city": [lyon_city for i in lyon_districts]
    })

    paris_districts = ["75101", "75102", "75103", "75104", "75105", "75106", "75107", "75108",
                       "75109", "75110", "75111", "75112", "75113", "75114", "75115", "75116",
                       "75117", "75118", "75119", "75120"]
    paris_city = "75056"
    paris = pd.DataFrame(data={
        "geo_code_district": paris_districts,
        "geo_code_city": [paris_city for i in paris_districts]
    })

    data = pd.concat([data, marseille, lyon, paris])
    data = data.drop_duplicates()

    data = data.replace({np.nan: None})
    data["year_cog"] = year_cog
    return data


def load_arrondissements_passage(pool):
    table_name = "insee_arrondissements_passage"
    cols_table = {
        "geo_code_district": "VARCHAR(12) NOT NULL",
        "geo_code_city": "VARCHAR(12) NOT NULL",

        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (geo_code_district, geo_code_city, year_cog) USING BTREE, KEY (geo_code_district) USING BTREE"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_cog_communes_from_csv(file_name, *missing_source)

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
        load_arrondissements_passage(None)

