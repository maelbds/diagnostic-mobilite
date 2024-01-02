import os
import pandas as pd
import numpy as np

from data_manager.db_functions import load_database
from data_manager.utilities import load_file


def download_files():
    # reference : "https://www.insee.fr/fr/statistiques/5359146#consulter"

    files = [{
        "name": "Dossier complet 2018 - COG 2021",
        "url": "https://diagnostic-mobilite.fr/data/2018/dossier_complet.zip", # not available anymore on INSEE website
        "dir": "data/2018",
        "zip_name": "dossier_complet2018.zip",
        "file_name": "dossier_complet.csv",
    }]

    [load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def load_data():
    variables = pd.read_csv("data/2018/variables_population_status.csv", sep=";", dtype=str)
    cols = variables["variables"].dropna().drop_duplicates().tolist()

    data = pd.read_csv(
        "data/2018/dossier_complet.csv",
        sep=";", dtype=str,
        usecols=cols)
    data.loc[:, data.columns != 'CODGEO'] = data.loc[:, data.columns != 'CODGEO'].astype("float").round()
    data = data.rename(columns={
        "C18_POP15P_CS7": "retired",
        "P18_SCOL0205": "scholars_2_5",
        "P18_SCOL0610": "scholars_6_10",
        "P18_SCOL1114": "scholars_11_14",
        "P18_SCOL1517": "scholars_15_17",
        "P18_ACTOCC15P": "employed",
        "P18_CHOM1564": "unemployed"
    })
    data["scholars_18"] = data["P18_SCOL1824"] + data["P18_SCOL2529"] + data["P18_SCOL30P"]

    data["other"] = data["P18_POP"] - data["P18_POP0014"] - data["retired"] - data["employed"] \
                    - data["unemployed"] - data["scholars_15_17"] - data["scholars_18"]
    data["other"] = data["other"].apply(lambda x: max(0, x))

    data.drop(columns=["P18_SCOL1824", "P18_SCOL2529", "P18_SCOL30P", "P18_POP0014", "P18_POP", "C18_PMEN"], inplace=True)

    data["year_data"] = "2018"
    data["year_cog"] = "2021"

    data = data.replace({np.nan: None})
    return data


def load_dossier_complet_status(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = load_data()

    cols_table = {
        "CODGEO": "VARCHAR(12) NOT NULL",

        "employed": "INT(11) NULL DEFAULT NULL",
        "unemployed": "INT(11) NULL DEFAULT NULL",
        "retired": "INT(11) NULL DEFAULT NULL",
        "scholars_2_5": "INT(11) NULL DEFAULT NULL",
        "scholars_6_10": "INT(11) NULL DEFAULT NULL",
        "scholars_11_14": "INT(11) NULL DEFAULT NULL",
        "scholars_15_17": "INT(11) NULL DEFAULT NULL",
        "scholars_18": "INT(11) NULL DEFAULT NULL",
        "other": "INT(11) NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (CODGEO, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.max_rows', 60)
    pd.set_option('display.width', 4000)

    data = load_data()
    print(data)

    # to prevent from unuseful loading data
    security = False
    if not security:
        load_dossier_complet_status(None, "insee_dossier_complet_status")

