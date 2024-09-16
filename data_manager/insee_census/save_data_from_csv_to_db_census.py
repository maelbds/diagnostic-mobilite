import pandas as pd
import numpy as np
import os

from data_manager.db_functions import load_database
from data_manager.insee_census.prepare_census import prepare_census
from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.utilities import load_file, download_url


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_data}",
        "zip_name": f"census{year_data}.zip",
        "file_name": f"FD_INDCVI_{year_data}.csv",
    }

    return load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"])


def get_census_from_csv_and_load(file_name, load, id, name, table_name, label, link, reference, year_data, year_cog):
    cols = ["CANTVILLE", "NUMMI", "AGED", "COUPLE", "CS1", "DEPT", "ETUD", "ILETUD", "ILT", "INPER", "IPONDI",
            "IRIS", "LIENF", "MOCO", "NENFR", "SEXE", "TACT", "TP", "TRANS", "TYPMR", "VOIT"]
    #data = pd.read_csv(file_name, sep=";", dtype=str, usecols=cols, low_memory=True)

    i = 0
    chunksize = 1000000

    with pd.read_csv(file_name, sep=";", dtype=str, usecols=cols, low_memory=True, chunksize=chunksize) as reader:
        for data in reader:
            print(f"-- chunk {i}")

            mask_can = data["CANTVILLE"].isin(["7915", "7901", "7903", "7905", "7909", "7914", "7999"])
            # data = data.loc[mask_can]

            data, cols = prepare_census(data)

            data["year_data"] = year_data
            data["year_cog"] = year_cog
            data.reset_index(drop=True, inplace=True)
            data["id"] = data.index + chunksize * i
            data = data.replace({np.nan: None})
            cols = data.columns.tolist()
            data = data[cols[-1:] + cols[:-1]]

            load(data)
            i += 1
    return


def load_census(pool):
    table_name = "insee_census"
    cols_table = {
        "id": "INT(11) NOT NULL",
        "CANTVILLE": "VARCHAR(50) NOT NULL",
        "NUMMI": "VARCHAR(50) NULL DEFAULT NULL",
        "AGED": "VARCHAR(50) NULL DEFAULT NULL",
        "COUPLE": "VARCHAR(50) NULL DEFAULT NULL",
        "CS1": "VARCHAR(50) NULL DEFAULT NULL",
        "DEPT": "VARCHAR(50) NULL DEFAULT NULL",
        "ETUD": "VARCHAR(50) NULL DEFAULT NULL",
        "ILETUD": "VARCHAR(50) NULL DEFAULT NULL",
        "ILT": "VARCHAR(50) NULL DEFAULT NULL",
        "INPER": "VARCHAR(50) NULL DEFAULT NULL",
        "IPONDI": "VARCHAR(50) NULL DEFAULT NULL",
        "IRIS": "VARCHAR(50) NULL DEFAULT NULL",
        "LIENF": "VARCHAR(50) NULL DEFAULT NULL",
        "MOCO": "VARCHAR(50) NULL DEFAULT NULL",
        "NENFR": "VARCHAR(50) NULL DEFAULT NULL",
        "SEXE": "VARCHAR(50) NULL DEFAULT NULL",
        "TACT": "VARCHAR(50) NULL DEFAULT NULL",
        "TP": "VARCHAR(50) NULL DEFAULT NULL",
        "TRANS": "VARCHAR(50) NULL DEFAULT NULL",
        "TYPMR": "VARCHAR(50) NULL DEFAULT NULL",
        "VOIT": "VARCHAR(50) NULL DEFAULT NULL",

        "id_census_hh": "VARCHAR(20) NULL DEFAULT NULL",
        "nb_child": "INT(2) NULL DEFAULT NULL",
        "status": "VARCHAR(15) NULL DEFAULT NULL",
        "work_within_commune": "INT(1) NULL DEFAULT NULL",
        "hh_type": "INT(1) NULL DEFAULT NULL",
        "nb_car": "INT(1) NULL DEFAULT NULL",
        "csp": "INT(1) NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (id, year_data) USING BTREE, KEY (CANTVILLE) USING BTREE"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"],
                              ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)

        def load(data):
            load_database(pool, table_name, data, cols_table, keys)

        get_census_from_csv_and_load(file_name, load, *missing_source)

        os.remove(file_name)
        save_source(pool, *missing_source)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_census(None)
