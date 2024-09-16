import pandas as pd

from data_manager.db_functions import create_new_table, empty_table, load_table


def load_aav_communes_cat(pool):
    table_name = "insee_aav_communes_cat"

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

    create_new_table(pool, table_name, cols_table, keys)
    empty_table(pool, table_name)
    load_table(pool, table_name, data, cols_table)


def load_aav_types(pool):
    table_name = "insee_aav_types"

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

    create_new_table(pool, table_name, cols_table, keys)
    empty_table(pool, table_name)
    load_table(pool, table_name, data, cols_table)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = False
    if not security:
        load_aav_communes_cat(None)
        load_aav_types(None)
