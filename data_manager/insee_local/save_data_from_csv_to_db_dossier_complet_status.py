import pandas as pd
import numpy as np
import os

from data_manager.db_functions import load_database
from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.utilities import load_file


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_data}",
        "zip_name": f"{name}_{year_data}.zip",
        "file_name": "dossier_complet.csv",
    }

    return load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"])


def get_data_from_csv(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    variables = pd.read_csv("data/variables_dossier_complet_status.csv", sep=";", dtype=str)
    cols = variables["variables"].dropna().drop_duplicates().tolist()
    cols = [col.replace("P18_", f"P{year_data[2:]}_").replace("C18_", f"C{year_data[2:]}_") for col in cols]

    data = pd.read_csv(file_name, sep=";", dtype=str, usecols=lambda x: x in cols)
    data.loc[:, data.columns != 'CODGEO'] = data.loc[:, data.columns != 'CODGEO'].astype("float").round()

    data = data.rename(columns=lambda name: name.replace(f"P{year_data[2:]}_", "").replace(f"C{year_data[2:]}_", ""))
    data = data.rename(columns={
        "POP15P_CS7": "retired",
        "SCOL0205": "scholars_2_5",
        "SCOL0610": "scholars_6_10",
        "SCOL1114": "scholars_11_14",
        "SCOL1517": "scholars_15_17",
        "ACTOCC15P": "employed",
        "CHOM1564": "unemployed"
    })
    data["scholars_18"] = data["SCOL1824"] + data["SCOL2529"] + data["SCOL30P"]

    data["other"] = data["POP"] - data["employed"] - data["unemployed"] - data["retired"] \
                    - data["scholars_2_5"] - data["scholars_6_10"] - data["scholars_11_14"] \
                    - data["scholars_15_17"] - data["scholars_18"]
    data["other"] = data["other"].apply(lambda x: max(0, x))

    data.drop(columns=["SCOL1824", "SCOL2529", "SCOL30P", "POP0014", "POP", "PMEN"], inplace=True)

    data["year_data"] = year_data
    data["year_cog"] = year_cog

    data = data.replace({np.nan: None})
    return data


def load_dossier_complet_status(pool):
    table_name = "insee_dossier_complet_status"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"],
                              ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_data_from_csv(file_name, *missing_source)

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

        os.remove(file_name)
        save_source(pool, *missing_source)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.max_rows', 60)
    pd.set_option('display.width', 4000)

    # to prevent from unuseful loading data
    security = False
    if not security:
        load_dossier_complet_status(None)
