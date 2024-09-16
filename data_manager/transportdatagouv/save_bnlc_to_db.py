import os

import pandas as pd
import numpy as np
from datetime import date

from data_manager.db_functions import create_new_table, empty_table, load_table
from data_manager.utilities import download_url


def download_files():
    # reference : "https://transport.data.gouv.fr/datasets/base-nationale-des-lieux-de-covoiturage"

    name = "Base nationale consolidée des lieux de covoiturage"
    url = "https://www.data.gouv.fr/fr/datasets/r/4fd78dee-e122-4c0d-8bf6-ff55d79f3af1"
    dir = "data/bnlc"
    file_name = "bnlc.csv"

    file_path = f"{dir}/{file_name}"

    if not os.path.isfile(file_path):
        print(f"{name} - downloading")
        download_url(url, file_path)
    else:
        print(f"{name} - already downloaded")


def get_bnlc_from_csv():
    # https://schema.data.gouv.fr/etalab/schema-lieux-covoiturage/latest/documentation.html#propriete-com-lieu
    cols = ["insee",
            "id_lieu", "nom_lieu",
            "type",
            "Xlong", "Ylat",
            "nbre_pl", "nbre_pmr",
            "proprio",
            "date_maj"]
    data = pd.read_csv(
        "data/bnlc/bnlc.csv",
        sep=",", dtype=str,
        usecols=cols)

    data["saved_on"] = date.today()
    data["id"] = data.index.values
    data = data.replace({np.nan: None})

    return data


def load_bnlc(pool):
    table_name = "transportdatagouv_bnlc"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()
    data = get_bnlc_from_csv()

    cols_table = {
        "id": "INT(11) NOT NULL",
        "id_lieu": "VARCHAR(50) NOT NULL",
        "nom_lieu": "VARCHAR(200) NULL DEFAULT NULL",
        "type": "VARCHAR(50) NULL DEFAULT NULL",
        "insee": "VARCHAR(11) NULL DEFAULT NULL",
        "Ylat": "FLOAT NULL DEFAULT NULL",
        "Xlong": "FLOAT NULL DEFAULT NULL",
        "nbre_pl": "INT(11) NULL DEFAULT NULL",
        "nbre_pmr": "INT(11) NULL DEFAULT NULL",
        "proprio": "VARCHAR(100) NULL DEFAULT NULL",
        "date_maj": "DATE NULL DEFAULT NULL",

        "saved_on": "DATE NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (id) USING BTREE, KEY (insee) USING BTREE"

    create_new_table(pool, table_name, cols_table, keys)
    empty_table(pool, table_name)
    load_table(pool, table_name, data, cols_table)

    os.remove("data/bnlc/bnlc.csv")


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_bnlc(None)
