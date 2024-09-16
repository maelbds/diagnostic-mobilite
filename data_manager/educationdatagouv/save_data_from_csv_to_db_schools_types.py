import pandas as pd
import numpy as np
import os

from data_manager.db_functions import create_new_table, empty_table, load_table


def get_schools_types_from_csv():
    types = pd.read_csv(
        "data/schools_types.csv",
        sep=";", dtype=str)

    types = types.replace({"\\N": None, np.nan: None})
    return types


def load_schools_types(pool):
    table_name = "educationdatagouv_schools_types"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    data = get_schools_types_from_csv()

    cols_table = {
        "id": "VARCHAR(50) NOT NULL",
        "name": "VARCHAR(255) NULL DEFAULT NULL",
        "id_type": "INT(11) NULL DEFAULT NULL",
        "id_category": "INT(11) NULL DEFAULT NULL",
        "daily_visitors": "INT(11) NULL DEFAULT NULL",
        "to_keep": "INT(11) NULL DEFAULT 0",
        "characteristic": "INT(11) NULL DEFAULT 0",
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

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_schools_types(None)
