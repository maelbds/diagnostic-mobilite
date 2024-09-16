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
    # reference : "https://transport.data.gouv.fr/datasets/base-nationale-consolidee-des-zones-a-faibles-emissions"

    name = "Base Nationale des Zones à Faibles Émissions"
    url = "https://www.data.gouv.fr/fr/datasets/r/673a16bf-49ec-4645-9da2-cf975d0aa0ea"
    dir = "data/zfe"
    file_name = "aires.geojson"

    file_path = f"{dir}/{file_name}"

    if not os.path.isfile(file_path):
        print(f"{name} - downloading")
        download_url(url, file_path)
    else:
        print(f"{name} - already downloaded")


def load_data():
    with open("data/zfe/aires.geojson", encoding="UTF-8") as data:
        geo = json.load(data)

    # geometry to wkb
    def geojson_to_wkb_geometry_collection(geojson):
        geom_coll = GeometryCollection([shape(geojson["geometry"])])
        geom_wkb = wkb.dumps(geom_coll)
        return geom_wkb

    data = pd.DataFrame([g["properties"] for g in geo["features"]])
    # variables https://schema.data.gouv.fr/schemas/etalab/schema-amenagements-cyclables/0.3.3/schema_amenagements_cyclables.json
    data = data[["id", "date_debut", "date_fin",
               "vp_critair", "vp_horaires",
               "vul_critair", "vul_horaires",
               "pl_critair", "pl_horaires",
               "autobus_autocars_critair", "autobus_autocars_horaires",
               "deux_rm_critair", "deux_rm_horaires"]]
    data["geo_code"] = [id.split("-")[0] for id in data["id"]]

    data["geometry"] = [geojson_to_wkb_geometry_collection(g) for g in geo["features"]]

    data["saved_on"] = date.today()
    data = data.replace({np.nan: None})

    return data


def load_zfe(pool):
    table_name = "transportdatagouv_zfe"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()
    data = load_data()

    cols_table = {
        "id": "VARCHAR(30) NOT NULL",
        "geo_code": "VARCHAR(15) NOT NULL",
        "date_debut": "DATE NULL DEFAULT NULL",
        "date_fin": "DATE NULL DEFAULT NULL",
        "vp_critair": "VARCHAR(50) NULL DEFAULT NULL",
        "vp_horaires": "VARCHAR(50) NULL DEFAULT NULL",
        "vul_critair": "VARCHAR(50) NULL DEFAULT NULL",
        "vul_horaires": "VARCHAR(50) NULL DEFAULT NULL",
        "pl_critair": "VARCHAR(50) NULL DEFAULT NULL",
        "pl_horaires": "VARCHAR(50) NULL DEFAULT NULL",
        "autobus_autocars_critair": "VARCHAR(50) NULL DEFAULT NULL",
        "autobus_autocars_horaires": "VARCHAR(50) NULL DEFAULT NULL",
        "deux_rm_critair": "VARCHAR(50) NULL DEFAULT NULL",
        "deux_rm_horaires": "VARCHAR(50) NULL DEFAULT NULL",

        "geometry": "GEOMETRYCOLLECTION NOT NULL",

        "saved_on": "DATE NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (id) USING BTREE, KEY (geo_code) USING BTREE"

    create_new_table(pool, table_name, cols_table, keys)
    empty_table(pool, table_name)
    load_table(pool, table_name, data, cols_table)

    os.remove("data/zfe/aires.geojson")


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)

    security = False
    if not security:
        load_zfe(None)

