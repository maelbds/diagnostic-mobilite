import pandas as pd
import numpy as np
import os

from data_manager.db_functions import create_new_table, empty_table, load_table


def get_data_from_csv():
    data = pd.read_csv(
        "types.csv",
        sep=";", dtype=str)

    return data


def load_types(pool):
    table_name = "types"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    data = get_data_from_csv()

    cols_table = {
        "id": "INT(5) NOT NULL",
        "name": "VARCHAR(100) NOT NULL",
        "id_category": "INT(2) NOT NULL"
    }
    keys = "PRIMARY KEY (id) USING BTREE"

    create_new_table(pool, table_name, cols_table, keys)
    empty_table(pool, table_name)
    load_table(pool, table_name, data, cols_table)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    print(get_data_from_csv())

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_types(None)


