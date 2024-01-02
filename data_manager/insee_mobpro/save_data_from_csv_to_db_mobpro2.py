"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import csv
import os

import pandas as pd

from data_manager.db_functions import load_database
from data_manager.insee_general.districts import get_districts
from data_manager.utilities import load_file


def download_files():
    # reference : "https://www.insee.fr/fr/statistiques/5395749?sommaire=5395764#consulter"

    files = [{
        "name": "INSEE MobPro 2018",
        "url": "https://www.insee.fr/fr/statistiques/fichier/5395749/RP2018_mobpro_csv.zip",
        "dir": "data/2018",
        "zip_name": "mobpro2018.zip",
        "file_name": "FD_MOBPRO_2018.csv",
    }]

    [load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def get_flows_from_csv():
    useful_cols = ["COMMUNE", "ARM", "DCFLT", "DCLT", "IPONDI", "TRANS", "TP", "SEXE", "CS1", "EMPL", "TYPMR"]
    mobpro = pd.read_csv("data/2018/FD_MOBPRO_2018.csv", sep=";", dtype=str, usecols=useful_cols)
    mobpro["IPONDI"] = mobpro["IPONDI"].astype("float64")

    # To merge foreign communes
    dcflt_mask = mobpro["DCLT"] == "99999"
    mobpro.loc[dcflt_mask, "DCLT"] = mobpro.loc[dcflt_mask, "DCFLT"]
    mobpro.drop(columns=["DCFLT"], inplace=True)

    districts = get_districts(None)
    mobpro = pd.merge(mobpro, districts, left_on="DCLT", right_on="district", how="left")
    mask_no_district = mobpro["city"].isna()
    mobpro.loc[~mask_no_district, "DCLT"] = mobpro.loc[~mask_no_district, "city"]

    flows = mobpro.groupby(by=["COMMUNE", "DCLT",
                               "TRANS", "TP", "SEXE", "CS1", "EMPL", "TYPMR"], as_index=False).sum()

    flows = flows.rename(columns={
        "COMMUNE": "CODGEO_home",
        "DCLT": "CODGEO_work",
        "IPONDI": "flow"
    })
    flows["year_data"] = "2018"
    flows["year_cog"] = "2020"
    flows["id"] = flows.index.values

    return flows


def load_flows_mobpro(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_flows_from_csv()

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


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    flows = get_flows_from_csv()
    print(flows)
    # to prevent from unuseful loading data
    security = True
    if not security:
        load_flows_mobpro(None, "insee_flows_mobpro")
