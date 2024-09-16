import json
import os

import pandas as pd
import numpy as np

from shapely.geometry import shape, GeometryCollection
from shapely import wkb
from datetime import date

from data_manager.db_functions import load_database, empty_table, create_new_table, load_table
from data_manager.utilities import load_file


def download_files():
    # reference : "https://transport.data.gouv.fr/datasets/stationnements-cyclables-issus-dopenstreetmap#dataset-resources"

    files = [{
        "name": "Base nationale du stationnement cyclable",
        "url": "https://geodatamine.fr/dump/bicycle_parking_geojson.zip",
        "dir": "data/cycle_parkings",
        "zip_name": "bicycle_parking_geojson.zip",
        "file_name": "data.geojson",
    }]

    [load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def get_cycle_parkings():
    with open("data/cycle_parkings/data.geojson", encoding="UTF-8") as data:
        geo = json.load(data)

    def handle_feature(geojson_feature):
        properties = geojson_feature["properties"]
        properties["lat"] = properties["coordonneesxy"][1]
        properties["lon"] = properties["coordonneesxy"][0]
        properties.pop("coordonneesxy")
        properties_df = pd.DataFrame(properties, index=[0])
        return properties_df

    features_df = [handle_feature(g) for g in geo["features"]]
    cycle_parkings = pd.concat(features_df, ignore_index=True)
    cycle_parkings["capacite"] = pd.to_numeric(cycle_parkings["capacite"], errors="coerce", downcast="integer")

    # variables https://schema.data.gouv.fr/schemas/etalab/schema-amenagements-cyclables/0.3.3/schema_amenagements_cyclables.json
    cycle_parkings = cycle_parkings[["id_local", "id_osm", "code_com", "lon", "lat",
                                     "capacite", "acces", "gestionnaire", "date_maj"]]

    cycle_parkings = cycle_parkings.replace({np.nan: None})
    cycle_parkings["saved_on"] = date.today()
    cycle_parkings["id"] = cycle_parkings.index.values

    return cycle_parkings


def load_cycle_parkings(pool):
    table_name = "transportdatagouv_cycle_parkings"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = get_cycle_parkings()

    cols_table = {
        "id": "INT(11) NOT NULL",
        "id_local": "VARCHAR(50) NOT NULL",
        "id_osm": "VARCHAR(50) NOT NULL",
        "code_com": "VARCHAR(11) NULL DEFAULT NULL",
        "lat": "FLOAT NULL DEFAULT NULL",
        "lon": "FLOAT NULL DEFAULT NULL",
        "capacite": "INT(11) NULL DEFAULT NULL",
        "acces": "VARCHAR(50) NULL DEFAULT NULL",
        "gestionnaire": "VARCHAR(200) NULL DEFAULT NULL",
        "date_maj": "DATE NULL DEFAULT NULL",

        "saved_on": "DATE NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (id) USING BTREE, KEY (code_com) USING BTREE"

    create_new_table(pool, table_name, cols_table, keys)
    empty_table(pool, table_name)
    load_table(pool, table_name, data, cols_table)

    os.remove("data/cycle_parkings/data.geojson")


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)


    security = True
    if not security:
        load_cycle_parkings(None)

