import json
import os

import pandas as pd
import numpy as np
from datetime import date

from shapely.geometry import shape, GeometryCollection
from shapely import wkb

from data_manager.db_functions import create_new_table, empty_table, load_table
from data_manager.utilities import download_url


def download_files():
    # reference : "https://transport.data.gouv.fr/datasets/amenagements-cyclables-france-metropolitaine"

    name = "Base Nationale des Aménagements Cyclables"
    url = "https://www.data.gouv.fr/fr/datasets/r/95239ec5-ede2-451b-b5e2-5fe147909bac"
    dir = "data/cycle_paths"
    file_name = "cycle_paths.geojson"

    file_path = f"{dir}/{file_name}"

    if not os.path.isfile(file_path):
        print(f"{name} - downloading")
        download_url(url, file_path)
    else:
        print(f"{name} - already downloaded")


def load_data():
    with open("data/cycle_paths/cycle_paths.geojson", encoding="UTF-8") as data:
        geo = json.load(data)

    # geometry to wkb
    def geojson_to_wkb_geometry_collection(geojson):
        geom_coll = GeometryCollection([shape(geojson["geometry"])])
        geom_wkb = wkb.dumps(geom_coll)
        return geom_wkb

    data = pd.DataFrame([g["properties"] for g in geo["features"]])
    # variables https://schema.data.gouv.fr/schemas/etalab/schema-amenagements-cyclables/0.3.3/schema_amenagements_cyclables.json
    data = data[["id_local", "id_osm", "code_com_d", "code_com_g", "ame_d", "ame_g",
                               "sens_g", "sens_d", "trafic_vit", "date_maj"]]

    data["geometry"] = [geojson_to_wkb_geometry_collection(g) for g in geo["features"]]

    data = data.replace({np.nan: None})
    data["saved_on"] = date.today()
    data["id"] = data.index.values

    return data


def load_cycle_paths(pool):
    table_name = "transportdatagouv_cycle_paths"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()
    data = load_data()

    cols_table = {
        "id": "INT(11) NOT NULL",
        "id_local": "VARCHAR(50) NOT NULL",
        "id_osm": "VARCHAR(50) NOT NULL",
        "code_com_d": "VARCHAR(11) NULL DEFAULT NULL",
        "code_com_g": "VARCHAR(11) NULL DEFAULT NULL",
        "ame_d": "VARCHAR(50) NULL DEFAULT NULL",
        "ame_g": "VARCHAR(50) NULL DEFAULT NULL",
        "sens_d": "VARCHAR(50) NULL DEFAULT NULL",
        "sens_g": "VARCHAR(50) NULL DEFAULT NULL",
        "trafic_vit": "INT(11) NULL DEFAULT NULL",
        "geometry": "GEOMETRYCOLLECTION NULL DEFAULT NULL",
        "date_maj": "DATE NULL DEFAULT NULL",

        "saved_on": "DATE NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (id) USING BTREE, KEY (code_com_d, code_com_g) USING BTREE"

    create_new_table(pool, table_name, cols_table, keys)
    empty_table(pool, table_name)
    load_table(pool, table_name, data, cols_table)

    os.remove("data/cycle_paths/cycle_paths.geojson")


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)

    security = True
    if not security:
        load_cycle_paths(None)

