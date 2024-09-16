import pandas as pd
import numpy as np
import os

from data_manager.db_functions import load_database
from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.utilities import download_url


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_data}",
        "zip_name": f"{name}_{year_data}.zip",
        "file_name": f"parc_vp_commune_2022.xlsx",
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
    cols = {
        "Code commune de résidence": "geo_code",
        #"Carburant": "fuel",
        "Crit'Air": "critair",
        year_data: "number",
    }
    data = pd.read_excel(file_name, sheet_name="Parcs communaux", skiprows=3, usecols=cols.keys(), dtype=str)
    data = data.rename(columns=cols)
    data["number"] = data["number"].astype(float)

    critair_labels = {
        "Crit'Air E": "elec",
        "Crit'Air 1": "critair1",
        "Crit'Air 2": "critair2",
        "Crit'Air 3": "critair3",
        "Crit'Air 4": "critair4",
        "Crit'Air 5": "critair5",
        "Non classé": "nc",
        "Inconnu": "unknown",
    }

    data = data.groupby(by=["geo_code", "critair"], as_index=False).sum()
    data = pd.get_dummies(data, columns=["critair"])
    data = data.rename(columns={f"critair_{key}": value for key, value in critair_labels.items()})

    for col in critair_labels.values():
        data[col] = data[col] * data["number"]

    data = data.drop(columns=["number"])
    data = data.groupby("geo_code", as_index=False).sum().round()

    data["year_data"] = year_data
    data["year_cog"] = year_cog

    data = data.replace({np.nan: None})
    return data


def load_critair(pool):
    table_name = "rsvero_critair"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"],
                              ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_data_from_csv(file_name, *missing_source)

        cols_table = {
            "geo_code": "VARCHAR(12) NOT NULL",

            "critair1": "INT(11) NULL DEFAULT NULL",
            "critair2": "INT(11) NULL DEFAULT NULL",
            "critair3": "INT(11) NULL DEFAULT NULL",
            "critair4": "INT(11) NULL DEFAULT NULL",
            "critair5": "INT(11) NULL DEFAULT NULL",
            "elec": "INT(11) NULL DEFAULT NULL",
            "nc": "INT(11) NULL DEFAULT NULL",
            "unknown": "INT(11) NULL DEFAULT NULL",

            "year_data": "VARCHAR(12) NOT NULL",
            "year_cog": "VARCHAR(12) NOT NULL",
        }
        keys = "PRIMARY KEY (geo_code, year_data) USING BTREE"

        load_database(pool, table_name, data, cols_table, keys)

        os.remove(file_name)
        save_source(pool, *missing_source)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    # to prevent from unuseful loading data
    security = False
    if not security:
        load_critair(None)
