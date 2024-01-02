import os
import pandas as pd

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


def get_universities_types_from_csv():
    type_cols = ["Code type", "Type"]
    type = pd.read_csv(
        "data/2017/fr-esr-implantations_etablissements_d_enseignement_superieur_publics.csv",
        sep=";", dtype=str,
        usecols=type_cols)
    type = type.rename(columns={"Code type": "id_univ_type", "Type": "name_univ_type"})
    type = type.dropna()
    type["id_type"] = 58
    type["id_category"] = 1
    type["characteristic"] = 1
    type = type.drop_duplicates()
    type = type.sort_values(by="id_univ_type")
    return type


def load_universities_types(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_universities_types_from_csv()

    cols_table = {
        "id_univ_type": "VARCHAR(50) NOT NULL",
        "name_univ_type": "VARCHAR(255) NULL DEFAULT NULL",
        "id_type": "INT(11) NULL DEFAULT NULL",
        "id_category": "INT(11) NULL DEFAULT NULL",
        "characteristic": "INT(11) NULL DEFAULT 0",
    }
    keys = "PRIMARY KEY (id_univ_type) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    univ_types = get_universities_types_from_csv()
    print(univ_types)

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_universities_types(None, "esrdatagouv_universities_types")
