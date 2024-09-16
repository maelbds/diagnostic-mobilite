import pandas as pd
import numpy as np
import os

from data_manager.db_functions import load_database
from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.util_districts import get_districts_to_city_dict
from data_manager.utilities import load_file, download_url


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_data}",
        "zip_name": f"{name}_{year_data}.zip",
        "file_name": f"fr-esr-implantations_etablissements_d_enseignement_superieur_publics.csv",
    }

    file_path = f"{f['dir']}/{f['file_name']}"

    if not os.path.isfile(file_path):
        print(f"{f['name']} - downloading")
        download_url(f['url'], file_path)
        return file_path
    else:
        print(f"{f['name']} - already downloaded")
        return file_path


def get_data_from_csv(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    cols = ["Code commune",
            "Implantation", "Code de l'implantation", "Géolocalisation", "Effectif d'étudiants inscrits",
            "Nature", "Code nature", "Type", "Code type",
            "Code de l'unité de rattachement", "Unité de rattachement",
            "type de l'établissement siège", "Code de l'établissement siège", "Etablissement siège"]

    data = pd.read_csv(file_name, sep=";", dtype=str, usecols=lambda x: x in cols)

    mask_type = data["Code type"].isin(["UNIV", "ING", "FORP", "CFA", "CNED", "PBAC"])
    data = data.loc[mask_type]

    data = data.dropna(subset=["Géolocalisation"])
    data["lat"] = data["Géolocalisation"].apply(lambda x: x.split(", ")[0])
    data["lon"] = data["Géolocalisation"].apply(lambda x: x.split(", ")[1])
    data = data.drop(columns=["Géolocalisation"])

    data = data.rename(columns={"Code commune": "geo_code",
                                "Code de l'implantation": "id",
                                "Implantation": "name",
                                "Effectif d'étudiants inscrits": "student_nb",
                                "Nature": "nature",
                                "Code nature": "code_nature",
                                "Type": "type",
                                "Code type": "code_type",
                                "Code de l'unité de rattachement": "unit_id",
                                "Unité de rattachement": "unit_name",
                                "type de l'établissement siège": "etab_type",
                                "Code de l'établissement siège": "etab_id",
                                "Etablissement siège": "etab_name"})

    data["geo_code"] = data["geo_code"].replace(to_replace=get_districts_to_city_dict())
    data["name"] = data["name"].apply(lambda x: x.lower().title() if type(x) is str else "")
    data["unit_name"] = data["unit_name"].apply(lambda x: x.lower().title() if type(x) is str else "")
    data["etab_name"] = data["etab_name"].apply(lambda x: x.lower().title() if type(x) is str else "")

    data = data.drop_duplicates(subset="id")
    data = data[["id", "name", "geo_code", "student_nb", "lat", "lon", "code_type"]]

    data["year_data"] = year_data
    data["year_cog"] = year_cog
    data["id"] = data.index.values

    data = data.replace({np.nan: None})
    return data


def load_universities(pool):
    table_name = "esrdatagouv_universities"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_data_from_csv(file_name, *missing_source)

        cols_table = {
            "id": "INT(11) NOT NULL",
            "geo_code": "VARCHAR(12) NULL DEFAULT NULL",
            "name": "VARCHAR(255) NULL DEFAULT NULL",
            "code_type": "VARCHAR(50) NULL DEFAULT NULL",
            "student_nb": "INT(10) NULL DEFAULT NULL",
            "lat": "FLOAT NULL DEFAULT NULL",
            "lon": "FLOAT NULL DEFAULT NULL",

            "year_data": "VARCHAR(12) NULL DEFAULT NULL",
            "year_cog": "VARCHAR(12) NULL DEFAULT NULL",
        }
        keys = "PRIMARY KEY (id, year_data) USING BTREE, KEY (geo_code) USING BTREE"

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
        load_universities(None)
