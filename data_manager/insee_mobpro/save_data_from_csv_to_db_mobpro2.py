import pandas as pd
import numpy as np
import os

from data_manager.db_functions import load_database
from data_manager.insee_general.districts import get_districts
from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.utilities import load_file


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_data}",
        "zip_name": f"{name}_{year_data}.zip",
        "file_name": f"FD_MOBPRO_{year_data}.csv",
    }

    return load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"])


def get_data_from_csv(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    cols = ["COMMUNE", "ARM", "DCFLT", "DCLT", "IPONDI", "TRANS", "TP", "SEXE", "CS1", "EMPL", "TYPMR"]

    data = pd.read_csv(file_name, sep=";", dtype=str, usecols=cols)
    data["IPONDI"] = data["IPONDI"].astype("float64")

    # To merge foreign communes
    dcflt_mask = data["DCLT"] == "99999"
    data.loc[dcflt_mask, "DCLT"] = data.loc[dcflt_mask, "DCFLT"]
    data.drop(columns=["DCFLT"], inplace=True)

    districts = get_districts(None)
    data = pd.merge(data, districts, left_on="DCLT", right_on="district", how="left")
    mask_no_district = data["city"].isna()
    data.loc[~mask_no_district, "DCLT"] = data.loc[~mask_no_district, "city"]

    data = data.groupby(by=["COMMUNE", "DCLT",
                               "TRANS", "TP", "SEXE", "CS1", "EMPL", "TYPMR"], as_index=False).sum()

    data = data.rename(columns={
        "COMMUNE": "CODGEO_home",
        "DCLT": "CODGEO_work",
        "IPONDI": "flow"
    })
    data["year_data"] = year_data
    data["year_cog"] = year_cog
    data["id"] = data.index.values

    data = data.replace({np.nan: None})
    return data


def load_mobpro_flows(pool):
    table_name = "insee_mobpro_flows"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_data_from_csv(file_name, *missing_source)

        cols_table = {
            "id": "INT(11) NOT NULL",
            "CODGEO_home": "VARCHAR(12) NOT NULL",
            "CODGEO_work": "VARCHAR(12) NOT NULL",
            "TRANS": "VARCHAR(5) NULL DEFAULT NULL",
            "TP": "VARCHAR(5) NULL DEFAULT NULL",
            "SEXE": "VARCHAR(5) NULL DEFAULT NULL",
            "CS1": "VARCHAR(5) NULL DEFAULT NULL",
            "EMPL": "VARCHAR(5) NULL DEFAULT NULL",
            "TYPMR": "VARCHAR(5) NULL DEFAULT NULL",
            "flow": "FLOAT NULL DEFAULT NULL",

            "year_data": "VARCHAR(12) NOT NULL",
            "year_cog": "VARCHAR(12) NOT NULL",
        }
        keys = "PRIMARY KEY (id, year_data) USING BTREE, KEY (CODGEO_home) USING BTREE, KEY (CODGEO_work) USING BTREE"

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
        load_mobpro_flows(None)
