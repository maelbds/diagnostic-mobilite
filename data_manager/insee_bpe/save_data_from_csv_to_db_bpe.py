import pandas as pd
import numpy as np
from pyproj import Transformer
import os

from data_manager.db_functions import load_database
from data_manager.sources.sources import missing_sources_for_table, save_source
from data_manager.util_districts import get_districts_to_city_dict
from data_manager.utilities import load_file


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_data}",
        "zip_name": f"{name}_{year_data}.zip",
        "file_name": f"bpe{year_data[2:]}_ensemble_xy.csv",
    }

    return load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"])


def get_data_from_csv(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    cols = ["DCIRIS", "LAMBERT_X", "LAMBERT_Y", "QUALITE_XY", "TYPEQU"]

    data = pd.read_csv(file_name, sep=";", dtype=str, usecols=lambda x: x in cols)
    data = data.astype({"LAMBERT_X": "float64", "LAMBERT_Y": "float64"})

    # Remove IRIS and keep only geocode :
    data["geo_code"] = [dciris[:5] for dciris in data["DCIRIS"]]
    data["geo_code"] = data["geo_code"].replace(to_replace=get_districts_to_city_dict())

    # Lambert to Geodetic coordinates system :
    transformer = Transformer.from_crs("epsg:2154",  # Lambert 93
                                       "epsg:4326")  # World Geodetic System (lat/lon)
    def lambert_to_geo(x, y):
        lat, lon = transformer.transform(x, y)
        return lat, lon

    data["coords"] = [lambert_to_geo(x, y) for x, y in zip(data["LAMBERT_X"], data["LAMBERT_Y"])]
    data["lat"] = [c[0] for c in data["coords"]]
    data["lon"] = [c[1] for c in data["coords"]]

    data = data.rename(columns={
        "TYPEQU": "id_type",
        "QUALITE_XY": "quality"})

    data = data.drop(columns=["LAMBERT_X", "LAMBERT_Y", "DCIRIS", "coords"])

    data["year_data"] = year_data
    data["year_cog"] = year_cog
    data["id"] = data.index.values

    data = data.replace({np.nan: None})
    return data


def load_bpe(pool):
    table_name = "insee_bpe"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_data_from_csv(file_name, *missing_source)

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
        keys = "PRIMARY KEY (id, year_data) USING BTREE, KEY (geo_code) USING BTREE"

        load_database(pool, table_name, data, cols_table, keys)

        os.remove(file_name)
        save_source(pool, *missing_source)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = False
    if not security:
        load_bpe(None)


