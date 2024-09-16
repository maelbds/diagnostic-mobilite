import pandas as pd
import numpy as np
import os

from data_manager.db_functions import create_new_table, load_table, empty_table
from data_manager.utilities import download_url


def download_files():
    # reference : "https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-implantations_etablissements_d_enseignement_superieur_publics/export/?disjunctive.bcnag_n_nature_uai_libelle_editi&disjunctive.services&disjunctive.type_uai&disjunctive.nature_uai"

    name = "Gares de voyageurs SNCF 2024"
    url = "https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/referentiel-gares-voyageurs/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
    dir = "data/2024"
    file_name = "referentiel-gares-voyageurs.csv"

    file_path = f"{dir}/{file_name}"

    if not os.path.isfile(file_path):
        print(f"{name} - downloading")
        download_url(url, file_path)
    else:
        print(f"{name} - already downloaded")


def get_stations_from_csv():
    cols = ["Code gare",
            "Code Commune", "Code département",
            "Longitude", "Latitude",
            "Intitulé gare"]
    data = pd.read_csv(
        "data/2024/referentiel-gares-voyageurs.csv",
        sep=";", dtype=str,
        usecols=cols)

    data["geo_code"] = data["Code département"] + data["Code Commune"]

    data = data.drop_duplicates(subset=["Code gare"])
    data = data.drop(columns=["Code département", "Code Commune"])

    data = data.rename(columns={"Code gare": "id",
                                "Intitulé gare": "name",
                                "Longitude": "lon",
                                "Latitude": "lat"})

    data["year_data"] = "2024"
    data["year_cog"] = "2023"
    data = data.replace({np.nan: None})

    return data


def load_railway_stations(pool):
    table_name = "sncf_stations"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_stations_from_csv()

    cols_table = {
        "id": "VARCHAR(11) NOT NULL",
        "geo_code": "VARCHAR(12) NULL DEFAULT NULL",
        "name": "VARCHAR(255) NULL DEFAULT NULL",
        "lat": "FLOAT NULL DEFAULT NULL",
        "lon": "FLOAT NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NULL DEFAULT NULL",
        "year_cog": "VARCHAR(12) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (id, year_data) USING BTREE, KEY (geo_code) USING BTREE"

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
        load_railway_stations(None)
