import os

import pandas as pd
import numpy as np
from shapely import wkb
from datetime import date

from data_manager.database_connection.sql_connect import mariadb_connection

from shapely.geometry import shape, Point

from data_manager.db_functions import create_new_table, empty_table, load_table
from data_manager.utilities import download_url


def download_files():
    # reference : "https://transport.data.gouv.fr/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques"

    name = "Infrastructures de Recharge pour Véhicules Électriques - IRVE"
    url = "https://www.data.gouv.fr/fr/datasets/r/eb76d20a-8501-400e-b336-d85724de5435"
    dir = "data/irve"
    file_name = "irve.csv"

    file_path = f"{dir}/{file_name}"

    if not os.path.isfile(file_path):
        print(f"{name} - downloading")
        download_url(url, file_path)
    else:
        print(f"{name} - already downloaded")


def get_commune_outline(pool):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT geo_code, outline  
                FROM ign_commune_outline 
                WHERE year_cog = ?""", ["2023"])
    result = list(cur)
    conn.close()

    def wkb_to_geojson(wkb_geom):
        geom_collection = wkb.loads(wkb_geom)
        geom = geom_collection.__geo_interface__
        return geom

    communes = pd.DataFrame(result, columns=["geo_code", "geometry"])
    communes["shape"] = [shape(wkb_to_geojson(g)) for g in communes["geometry"]]
    communes["minx"] = [s.bounds[0] for s in communes["shape"]]
    communes["miny"] = [s.bounds[1] for s in communes["shape"]]
    communes["maxx"] = [s.bounds[2] for s in communes["shape"]]
    communes["maxy"] = [s.bounds[3] for s in communes["shape"]]

    communes.drop(columns=["geometry"], inplace=True)
    return communes


def get_irve_from_csv():
    # https://schema.data.gouv.fr/etalab/schema-irve-statique/latest/documentation.html
    cols = ["code_insee_commune",
            "id_station_itinerance", "nom_station", "implantation_station", "coordonneesXY",
            "nom_operateur", "nom_amenageur",
            "nbre_pdc", "id_pdc_itinerance", "puissance_nominale", "prise_type_ef", "prise_type_2",
            "prise_type_combo_ccs", "prise_type_chademo", "prise_type_autre",
            "condition_acces",
            "date_maj"]
    data = pd.read_csv(
        "data/irve/irve.csv",
        sep=",", dtype=str,
        usecols=cols)

    data["lat"] = [float(coords.replace(" ", "")[1:-1].split(",")[1]) for coords in data["coordonneesXY"]]
    data["lon"] = [float(coords.replace(" ", "")[1:-1].split(",")[0]) for coords in data["coordonneesXY"]]
    data = data.drop(columns=["coordonneesXY"])

    print(data)
    print(data[data["code_insee_commune"] == "34202"])

    mask_no_geocode = data["code_insee_commune"].isna()
    print(f"{sum(mask_no_geocode)} irve sans code commune")
    print('recherche des codes')

    communes_shapes = get_commune_outline(None)
    def find_geocode(lat, lon):
        mask_communes_not_to_check = (communes_shapes["miny"] > lat) | \
                                     (communes_shapes["maxy"] < lat) | \
                                     (communes_shapes["minx"] > lon) | \
                                     (communes_shapes["maxx"] < lon)

        communes_to_check = communes_shapes[~mask_communes_not_to_check]
        point = Point(lon, lat)
        mask_is_in = [s.contains(point) for s in communes_to_check["shape"]]
        if sum(mask_is_in) > 0:
            return communes_to_check.loc[mask_is_in, "geo_code"].iloc[0]
        else:
            return None

    data.loc[mask_no_geocode, "code_insee_commune"] = [find_geocode(lat, lon) for lat, lon in zip(
        data.loc[mask_no_geocode, "lat"],
        data.loc[mask_no_geocode, "lon"]
    )]
    print(f"{sum(data['code_insee_commune'].isna())} irve sans code commune")

    data["saved_on"] = date.today()
    data["id"] = data.index.values
    data = data.replace({np.nan: None})


    print(data)
    print(data[data["code_insee_commune"] == "34202"])

    return data


def load_irve(pool):
    table_name = "transportdatagouv_irve"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()
    data = get_irve_from_csv()

    cols_table = {
        "id": "INT(11) NOT NULL",
        "id_station_itinerance": "VARCHAR(50) NOT NULL",
        "id_pdc_itinerance": "VARCHAR(50) NOT NULL",
        "nom_station": "VARCHAR(255) NULL DEFAULT NULL",
        "nom_operateur": "VARCHAR(255) NULL DEFAULT NULL",
        "nom_amenageur": "VARCHAR(255) NULL DEFAULT NULL",
        "implantation_station": "VARCHAR(50) NULL DEFAULT NULL",
        "code_insee_commune": "VARCHAR(11) NULL DEFAULT NULL",
        "lat": "FLOAT NULL DEFAULT NULL",
        "lon": "FLOAT NULL DEFAULT NULL",
        "nbre_pdc": "INT(11) NULL DEFAULT NULL",
        "puissance_nominale": "INT(11) NULL DEFAULT NULL",
        "prise_type_ef": "VARCHAR(5) NULL DEFAULT NULL",
        "prise_type_2": "VARCHAR(5) NULL DEFAULT NULL",
        "prise_type_combo_ccs": "VARCHAR(5) NULL DEFAULT NULL",
        "prise_type_chademo": "VARCHAR(5) NULL DEFAULT NULL",
        "prise_type_autre": "VARCHAR(5) NULL DEFAULT NULL",
        "condition_acces": "VARCHAR(50) NULL DEFAULT NULL",
        "date_maj": "DATE NULL DEFAULT NULL",

        "saved_on": "DATE NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (id) USING BTREE, KEY (code_insee_commune) USING BTREE"

    create_new_table(pool, table_name, cols_table, keys)
    empty_table(pool, table_name)
    load_table(pool, table_name, data, cols_table)

    os.remove("data/irve/irve.csv")


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = False
    if not security:
        load_irve(None)
