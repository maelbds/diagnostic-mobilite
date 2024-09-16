"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import os
import numpy as np
import pandas as pd

from data_manager.db_functions import load_database
from data_manager.insee_general.districts import get_districts
from data_manager.utilities import load_file


def download_files():
    # reference : "https://www.insee.fr/fr/statistiques/5395749?sommaire=5395764#consulter"

    files = [{
        "name": "INSEE MobPro (distance) 2019",
        "url": "https://www.data.gouv.fr/fr/datasets/r/452692fb-edf8-4dbd-a870-cb0e4230dc13",
        "dir": "data/2019",
        "zip_name": "mobpro_distance_2019.zip",
        "file_name": "depl_dom_trav_co2_2019.csv",
    }]

    [load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def get_flows_from_csv():
    useful_cols = ["LIEU_RESID", "LIEU_TRAV", "IPONDI", "MODTRANS", "TP", "SEXE", "CS1", "EMPL", "TYPMR", "DIST", "DUREE", "DIST_HEBDO"]
    mobpro = pd.read_csv("data/2019/depl_dom_trav_co2_2019.csv", sep=";", decimal=",", usecols=useful_cols)

    mobpro = mobpro.astype({
        "IPONDI": "float64",
        "LIEU_RESID": "str",
        "LIEU_TRAV": "str",
    })

    mobpro["LIEU_RESID"] = mobpro["LIEU_RESID"].apply(lambda x: "0" + x if len(x) == 4 else x)
    mobpro["LIEU_TRAV"] = mobpro["LIEU_TRAV"].apply(lambda x: "0" + x if len(x) == 4 else x)

    districts = get_districts(None).set_index("district")["city"].to_dict()
    mobpro["LIEU_RESID"] = mobpro["LIEU_RESID"].replace(districts)
    mobpro["LIEU_TRAV"] = mobpro["LIEU_TRAV"].replace(districts)

    mobpro = mobpro.groupby(["LIEU_RESID", "LIEU_TRAV", "MODTRANS", "TP", "SEXE", "CS1", "EMPL", "TYPMR"], as_index=False).agg(**{
        "IPONDI": pd.NamedAgg(column="IPONDI", aggfunc="sum"),
        "DIST": pd.NamedAgg(column="DIST", aggfunc="mean"),
        "DIST_HEBDO": pd.NamedAgg(column="DIST_HEBDO", aggfunc="mean"),
        "DUREE": pd.NamedAgg(column="DUREE", aggfunc="mean"),
    })

    mobpro = mobpro.rename(columns={
        "LIEU_RESID": "CODGEO_home",
        "LIEU_TRAV": "CODGEO_work",
        "MODTRANS": "TRANS",
        "IPONDI": "flow",
    })
    mobpro["year_data"] = "2019"
    mobpro["year_cog"] = "2021"
    mobpro["id"] = mobpro.index.values

    mobpro = mobpro.replace({np.nan: None})
    return mobpro


def load_flows_mobpro_distance(pool, table_name):
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

        "DIST": "FLOAT NULL DEFAULT NULL",
        "DIST_HEBDO": "FLOAT NULL DEFAULT NULL",
        "DUREE": "FLOAT NULL DEFAULT NULL",

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

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_flows_mobpro_distance(None, "insee_flows_mobpro_distance")
