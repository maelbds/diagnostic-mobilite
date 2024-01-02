import os

import pandas as pd
import numpy as np

from data_manager.db_functions import load_database
from data_manager.utilities import download_url


def download_files():
    # reference : "https://data.education.gouv.fr/explore/dataset/fr-en-adresse-et-geolocalisation-etablissements-premier-et-second-degre/export/?disjunctive.numero_uai&disjunctive.nature_uai&disjunctive.nature_uai_libe&disjunctive.code_departement&disjunctive.code_region&disjunctive.code_academie&disjunctive.code_commune&disjunctive.libelle_departement&disjunctive.libelle_region&disjunctive.libelle_academie&disjunctive.secteur_prive_code_type_contrat&disjunctive.secteur_prive_libelle_type_contrat&disjunctive.code_ministere&disjunctive.libelle_ministere"

    name = "Education Data Gouv écoles 2023"
    url = "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-adresse-et-geolocalisation-etablissements-premier-et-second-degre/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
    dir = "data/2023"
    file_name = "fr-en-adresse-et-geolocalisation-etablissements-premier-et-second-degre.csv"

    file_path = f"{dir}/{file_name}"

    if not os.path.isfile(file_path):
        print(f"{name} - downloading")
        download_url(url, file_path)
    else:
        print(f"{name} - already downloaded")


def get_schools_from_csv():
    cols = ["Code commune", "Appellation officielle", "Code nature", "Latitude", "Longitude", "Qualité d'appariement", "Code état établissement"]
    data = pd.read_csv(
        "data/2023/fr-en-adresse-et-geolocalisation-etablissements-premier-et-second-degre.csv",
        sep=";", dtype=str,
        usecols=cols)
    data = data.rename(columns={"Code commune": "geo_code",
                                "Appellation officielle": "name",
                                "Code nature": "id_type",
                                "Latitude": "lat",
                                "Longitude": "lon",
                                "Qualité d'appariement": "quality"})
    data = data[data["Code état établissement"] == "1"]

    data = data[data["quality"] != "Erreur"]
    data = data.drop(columns=["Code état établissement"])
    data = data.dropna(subset=["lat", "lon"])

    data["year_data"] = "2023"
    data["year_cog"] = "2023"

    data["id"] = data.index.values
    data = data.replace({np.nan: None})
    return data


def load_schools(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_schools_from_csv()

    cols_table = {
        "id": "INT(11) NOT NULL",
        "geo_code": "VARCHAR(12) NULL DEFAULT NULL",
        "name": "VARCHAR(255) NULL DEFAULT NULL",
        "id_type": "VARCHAR(50) NULL DEFAULT NULL",
        "lat": "FLOAT NULL DEFAULT NULL",
        "lon": "FLOAT NULL DEFAULT NULL",
        "quality": "VARCHAR(50) NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NULL DEFAULT NULL",
        "year_cog": "VARCHAR(12) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (id) USING BTREE, KEY (geo_code) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_schools(None, "educationdatagouv_schools")
