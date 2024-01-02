import os

import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.db_functions import load_database


def get_aav_from_file():
    aav_cols = ["AAV2020", "LIBAAV2020", "TAAV2017", "TDAAV2017", "NB_COM"]
    aav_communes_cols = ["CODGEO", "AAV2020", "CATEAAV2020"]

    insee_aav_communes = pd.read_excel("data/2022/aire_attraction_ville/AAV2020_au_01-01-2022.xlsx",
                                 sheet_name="Composition_communale", header=5, usecols=aav_communes_cols, dtype="str")
    insee_aav = pd.read_excel("data/2022/aire_attraction_ville/AAV2020_au_01-01-2022.xlsx",
                                 sheet_name="AAV2020", header=5, usecols=aav_cols, dtype="str")

    print(insee_aav_communes)
    print(insee_aav)

    return insee_aav_communes, insee_aav


def save_data_insee_aav_communes(insee_aav_communes):
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in insee_aav_communes.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in insee_aav_communes.columns]) + ")"

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_aav_communes """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in insee_aav_communes.iterrows()]

    conn.commit()
    conn.close()


def save_data_insee_aav(insee_aav):
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in insee_aav.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in insee_aav.columns]) + ")"

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_aav """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in insee_aav.iterrows()]

    conn.commit()
    conn.close()


def load_aav(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    insee_aav_communes, insee_aav = get_aav_from_file()

    insee_aav.rename(columns={n: n.replace("2020", "").replace("2017", "")
                              for n in insee_aav.columns}, inplace=True)
    insee_aav["year_data"] = "2020"
    insee_aav["year_cog"] = "2022"

    data = insee_aav

    cols_table = {
        "AAV": "VARCHAR(12) NOT NULL",
        "LIBAAV": "VARCHAR(255) NULL DEFAULT NULL",
        "TAAV": "VARCHAR(50) NULL DEFAULT NULL",
        "TDAAV": "VARCHAR(50) NULL DEFAULT NULL",
        "NB_COM": "INT(11) NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (AAV, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


def load_aav_communes(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    insee_aav_communes, insee_aav = get_aav_from_file()

    insee_aav_communes.rename(columns={n: n.replace("2020", "").replace("2017", "")
                                       for n in insee_aav_communes.columns}, inplace=True)
    insee_aav_communes["year_data"] = "2020"
    insee_aav_communes["year_cog"] = "2022"

    data = insee_aav_communes

    cols_table = {
        "CODGEO": "VARCHAR(12) NOT NULL",
        "AAV": "VARCHAR(12) NULL DEFAULT NULL",
        "CATEAAV": "VARCHAR(12) NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (CODGEO, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


def load_aav_communes_cat(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    data = pd.DataFrame({
        "CATEAAV": ["11", "12", "13", "20", "30"],
        "CATEAAV_name": ["Commune-centre",
                         "Autre commune du pôle principal",
                         "Commune d'un pôle secondaire",
                         "Commune de la couronne",
                         "Commune hors attraction des pôles"],
    })

    cols_table = {
        "CATEAAV": "VARCHAR(50) NOT NULL",
        "CATEAAV_name": "VARCHAR(50) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (CATEAAV) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


def load_aav_types(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    data = pd.DataFrame([
                {
                    "TAAV_TDAAV": "0",
                    "TAAV_TDAAV_name": "Commune hors attraction des villes"
                },
                {
                    "TAAV_TDAAV": "00",
                    "TAAV_TDAAV_name": "Commune hors attraction des villes"
                },
                {
                    "TAAV_TDAAV": "1",
                    "TAAV_TDAAV_name": "Aire de moins de 50 000 habitants"
                },
                {
                    "TAAV_TDAAV": "11",
                    "TAAV_TDAAV_name": "Aire de moins de 10 000 habitants"
                },
                {
                    "TAAV_TDAAV": "12",
                    "TAAV_TDAAV_name": "Aire de 10 000 à moins de 20 000 habitants"
                },
                {
                    "TAAV_TDAAV": "13",
                    "TAAV_TDAAV_name": "Aire de 20 000 à moins de 30 000 habitants"
                },
                {
                    "TAAV_TDAAV": "14",
                    "TAAV_TDAAV_name": "Aire de 30 000 à moins de 50 000 habitants"
                },
                {
                    "TAAV_TDAAV": "2",
                    "TAAV_TDAAV_name": "Aire de 50 000 à moins de 200 000 habitants"
                },
                {
                    "TAAV_TDAAV": "21",
                    "TAAV_TDAAV_name": "Aire de 50 000 à moins de 75 000 habitants"
                },
                {
                    "TAAV_TDAAV": "22",
                    "TAAV_TDAAV_name": "Aire de 75 000 à moins de 100 000 habitants"
                },
                {
                    "TAAV_TDAAV": "23",
                    "TAAV_TDAAV_name": "Aire de 100 000 à moins de 125 000 habitants"
                },
                {
                    "TAAV_TDAAV": "24",
                    "TAAV_TDAAV_name": "Aire de 125 000 à moins de 150 000 habitants"
                },
                {
                    "TAAV_TDAAV": "25",
                    "TAAV_TDAAV_name": "Aire de 150 000 à moins de 200 000 habitants"
                },
                {
                    "TAAV_TDAAV": "3",
                    "TAAV_TDAAV_name": "Aire de 200 000 à moins de 700 000 habitants"
                },
                {
                    "TAAV_TDAAV": "31",
                    "TAAV_TDAAV_name": "Aire de 200 000 à moins de 300 000 habitants"
                },
                {
                    "TAAV_TDAAV": "32",
                    "TAAV_TDAAV_name": "Aire de 300 000 à moins de 400 000 habitants"
                },
                {
                    "TAAV_TDAAV": "33",
                    "TAAV_TDAAV_name": "Aire de 400 000 à moins de 500 000 habitants"
                },
                {
                    "TAAV_TDAAV": "34",
                    "TAAV_TDAAV_name": "Aire de 500 000 à moins de 700 000 habitants"
                },
                {
                    "TAAV_TDAAV": "4",
                    "TAAV_TDAAV_name": "Aire de 700 000 habitants ou plus (hors Paris)"
                },
                {
                    "TAAV_TDAAV": "41",
                    "TAAV_TDAAV_name": "Aire de 700 000 à moins de 1 000 000 d’habitants"
                },
                {
                    "TAAV_TDAAV": "42",
                    "TAAV_TDAAV_name": "Aire de 1 000 000 d’habitants ou plus (hors Paris)"
                },
                {
                    "TAAV_TDAAV": "5",
                    "TAAV_TDAAV_name": "Aire de Paris"
                },
                {
                    "TAAV_TDAAV": "50",
                    "TAAV_TDAAV_name": "Aire de Paris"
                }
            ]
    )

    cols_table = {
        "TAAV_TDAAV": "VARCHAR(50) NOT NULL",
        "TAAV_TDAAV_name": "VARCHAR(50) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (TAAV_TDAAV) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    load_aav_types(None, "tot")
    exit()

    insee_aav_communes, insee_aav = get_aav_from_file()

    insee_aav_communes.rename(columns={n: n.replace("2020", "").replace("2017", "")
                                       for n in insee_aav_communes.columns}, inplace=True)
    insee_aav.rename(columns={n: n.replace("2020", "").replace("2017", "")
                              for n in insee_aav.columns}, inplace=True)

    insee_aav_communes["year_data"] = "2020"
    insee_aav_communes["year_cog"] = "2022"

    insee_aav["year_data"] = "2020"
    insee_aav["year_cog"] = "2022"

    print(insee_aav_communes)
    print(insee_aav)

    # to prevent from unuseful loading data
    security = True
    if not security:
        save_data_insee_aav(insee_aav)
        save_data_insee_aav_communes(insee_aav_communes)
