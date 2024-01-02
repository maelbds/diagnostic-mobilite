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


def get_school_types_from_csv():
    type_cols = ["Code nature", "Nature"]
    type = pd.read_csv(
        "data/2023/fr-en-adresse-et-geolocalisation-etablissements-premier-et-second-degre.csv",
        sep=";", dtype=str,
        usecols=type_cols)
    type = type.rename(columns={"Code nature": "id", "Nature": "name"})
    type = type.drop_duplicates()
    type = type.sort_values(by="id")

    type["id_category"] = 1

    mask_id_type_maternelle = type["id"] == "101"
    type.loc[mask_id_type_maternelle, "id_type"] = 35
    type.loc[mask_id_type_maternelle, "daily_visitors"] = 50
    mask_id_type_elementaire = type["id"] == "151"
    type.loc[mask_id_type_elementaire, "id_type"] = 33
    type.loc[mask_id_type_elementaire, "daily_visitors"] = 100
    mask_id_type_college = type["id"] == "340"
    type.loc[mask_id_type_college, "id_type"] = 36
    type.loc[mask_id_type_college, "daily_visitors"] = 200
    mask_id_type_lycee = type["id"].isin(["300", "301", "302", "306", "307", "320"])
    type.loc[mask_id_type_lycee, "id_type"] = 37
    type.loc[mask_id_type_lycee, "daily_visitors"] = 500

    mask_to_keep_characteristic = type["id"].isin(["101", "151", "300", "301", "302", "306", "307", "320", "340"])
    type.loc[mask_to_keep_characteristic, "to_keep"] = 1
    type.loc[mask_to_keep_characteristic, "characteristic"] = 1
    type["daily_visitors"] = type["daily_visitors"].fillna(50)

    type = type.replace({np.nan: None})

    return type


def load_school_types(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_school_types_from_csv()

    cols_table = {
        "id": "INT(11) NOT NULL",
        "name": "VARCHAR(255) NULL DEFAULT NULL",
        "id_type": "INT(11) NULL DEFAULT NULL",
        "id_category": "INT(11) NULL DEFAULT NULL",
        "daily_visitors": "INT(5) NULL DEFAULT NULL",
        "to_keep": "INT(11) NULL DEFAULT 0",
        "characteristic": "INT(11) NULL DEFAULT 0",
    }
    keys = "PRIMARY KEY (id) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    print(get_school_types_from_csv())

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_school_types(None, "educationdatagouv_schools_types")
