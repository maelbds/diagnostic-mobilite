import pandas as pd
import os

from data_manager.db_functions import create_new_table, empty_table, load_table


def get_data_from_csv():
    data = pd.read_csv(
        "data/all/modes.csv",
        sep=";", dtype=str)

    return data


def load_emd_modes(pool):
    table_name = "emd_modes"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    data = get_data_from_csv()

    cols_table = {
        "id": "VARCHAR(5) NOT NULL",
        "name_fr": "VARCHAR(50) NULL DEFAULT NULL",
        "id_main_mode": "INT(2) NOT NULL"
    }
    keys = "PRIMARY KEY (id) USING BTREE, KEY(id_main_mode) USING BTREE"

    create_new_table(pool, table_name, cols_table, keys)
    empty_table(pool, table_name)
    load_table(pool, table_name, data, cols_table)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_emd_modes(None)


