import os

import pandas as pd
from data_manager.db_functions import load_database


def load_arrondissements(pool):
    table_name = "insee_arrondissements"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    data = pd.DataFrame(
        [
            {
                "geo_code_district": "13201",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "13202",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "13203",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "13204",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "13205",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "13206",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "13207",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "13208",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "13209",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "13210",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "13211",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "13212",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "13213",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "13214",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "13215",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "13216",
                "geo_code_city": "13055"
            },
            {
                "geo_code_district": "69381",
                "geo_code_city": "69123"
            },
            {
                "geo_code_district": "69382",
                "geo_code_city": "69123"
            },
            {
                "geo_code_district": "69383",
                "geo_code_city": "69123"
            },
            {
                "geo_code_district": "69384",
                "geo_code_city": "69123"
            },
            {
                "geo_code_district": "69385",
                "geo_code_city": "69123"
            },
            {
                "geo_code_district": "69386",
                "geo_code_city": "69123"
            },
            {
                "geo_code_district": "69387",
                "geo_code_city": "69123"
            },
            {
                "geo_code_district": "69388",
                "geo_code_city": "69123"
            },
            {
                "geo_code_district": "69389",
                "geo_code_city": "69123"
            },
            {
                "geo_code_district": "75101",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75102",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75103",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75104",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75105",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75106",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75107",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75108",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75109",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75110",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75111",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75112",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75113",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75114",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75115",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75116",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75117",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75118",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75119",
                "geo_code_city": "75056"
            },
            {
                "geo_code_district": "75120",
                "geo_code_city": "75056"
            }
        ]
    )

    cols_table = {
        "geo_code_district": "VARCHAR(12) NOT NULL",
        "geo_code_city": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (geo_code_district, geo_code_city) USING BTREE"

    try:
        load_database(pool, table_name, data, cols_table, keys)
    except:
        "arrondissements already loaded"


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

