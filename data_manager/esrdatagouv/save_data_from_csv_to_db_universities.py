import pandas as pd
import numpy as np
import os

from data_manager.db_functions import load_database
from data_manager.utilities import download_url


def download_files():
    # reference : "https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-implantations_etablissements_d_enseignement_superieur_publics/export/?disjunctive.bcnag_n_nature_uai_libelle_editi&disjunctive.services&disjunctive.type_uai&disjunctive.nature_uai"

    name = "Enseignement supérieur universités 2017"
    url = "https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/fr-esr-implantations_etablissements_d_enseignement_superieur_publics/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
    dir = "data/2017"
    file_name = "fr-esr-implantations_etablissements_d_enseignement_superieur_publics.csv"

    file_path = f"{dir}/{file_name}"

    if not os.path.isfile(file_path):
        print(f"{name} - downloading")
        download_url(url, file_path)
    else:
        print(f"{name} - already downloaded")


def get_universities_from_csv():
    cols = ["Code commune",
            "Implantation", "Code de l'implantation", "Géolocalisation", "Effectif d'étudiants inscrits",
            "Nature", "Code nature", "Type", "Code type",
            "Code de l'unité de rattachement", "Unité de rattachement",
            "type de l'établissement siège", "Code de l'établissement siège", "Etablissement siège"]
    data = pd.read_csv(
        "data/2017/fr-esr-implantations_etablissements_d_enseignement_superieur_publics.csv",
        sep=";", dtype=str,
        usecols=cols)

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

    data["name"] = data["name"].apply(lambda x: x.lower().title() if type(x) is str else "")
    data["unit_name"] = data["unit_name"].apply(lambda x: x.lower().title() if type(x) is str else "")
    data["etab_name"] = data["etab_name"].apply(lambda x: x.lower().title() if type(x) is str else "")

    data = data.drop_duplicates(subset="id")
    data["id"] = data.index.values
    data = data[["id", "name", "geo_code", "student_nb", "lat", "lon", "code_type"]]

    data["year_data"] = "2017"
    data["year_cog"] = "2017"
    data = data.replace({np.nan: None})

    return data


def load_universities(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_universities_from_csv()

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


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    print(get_universities_from_csv())

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_universities(None, "esrdatagouv_universities")
