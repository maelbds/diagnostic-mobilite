import os

import pandas as pd
import numpy as np
from pyproj import Transformer
import time

from data_manager.db_functions import load_database
from data_manager.utilities import load_file


def download_files():
    # reference : "https://www.insee.fr/fr/statistiques/3568638?sommaire=3568656"

    files = [{
        "name": "INSEE BPE 2021",
        "url": "https://www.insee.fr/fr/statistiques/fichier/3568638/bpe21_ensemble_xy_csv.zip",
        "dir": "data/2021",
        "zip_name": "bpe2021.zip",
        "file_name": "bpe21_ensemble_xy.csv",
    }]

    [load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def get_bpe_from_csv():
    bpe_cols = ["DCIRIS", "LAMBERT_X", "LAMBERT_Y", "QUALITE_XY", "TYPEQU"]
    bpe = pd.read_csv(
        "data/2021/bpe21_ensemble_xy.csv",
        sep=";", dtype=str,
        usecols=bpe_cols)
    bpe = bpe.astype({"LAMBERT_X": "float64", "LAMBERT_Y": "float64"})

    # Remove IRIS and keep only geocode :
    bpe["geo_code"] = [dciris[:5] for dciris in bpe["DCIRIS"]]

    # Lambert to Geodetic coordinates system :
    transformer = Transformer.from_crs("epsg:2154",  # Lambert 93
                                       "epsg:4326")  # World Geodetic System (lat/lon)
    def lambert_to_geo(x, y):
        lat, lon = transformer.transform(x, y)
        return lat, lon

    bpe["coords"] = [lambert_to_geo(x, y) for x, y in zip(bpe["LAMBERT_X"], bpe["LAMBERT_Y"])]
    bpe["lat"] = [c[0] for c in bpe["coords"]]
    bpe["lon"] = [c[1] for c in bpe["coords"]]

    bpe = bpe.rename(columns={
        "TYPEQU": "id_type",
        "QUALITE_XY": "quality"})

    bpe = bpe.drop(columns=["LAMBERT_X", "LAMBERT_Y", "DCIRIS", "coords"])

    bpe["year_data"] = "2021"
    bpe["year_cog"] = "2021"
    bpe["id"] = bpe.index.values

    bpe = bpe.replace({np.nan: None})
    return bpe


def load_bpe(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_bpe_from_csv()

    cols_table = {
        "id": "INT(11) NOT NULL",
        "geo_code": "VARCHAR(12) NULL DEFAULT NULL",
        "id_type": "VARCHAR(50) NULL DEFAULT NULL",
        "lat": "FLOAT NULL DEFAULT NULL",
        "lon": "FLOAT NULL DEFAULT NULL",
        "quality": "VARCHAR(50) NULL DEFAULT NULL",
        "year_data": "VARCHAR(12) NULL DEFAULT NULL",
        "year_cog": "VARCHAR(12) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (id) USING BTREE, KEY (geo_code) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = False
    if not security:
        load_bpe(None, "insee_bpe")


