import pandas as pd
import os

from data_manager.db_functions import create_new_table, empty_table, load_table


def get_data_from_csv():
    data = pd.read_csv(
        "data/2018/reasons.csv",
        sep=";", dtype=str)

    return data


def load_emp_reasons(pool):
    table_name = "emp_reasons"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    data = get_data_from_csv()

    cols_table = {
        "id_emp": "VARCHAR(5) NOT NULL",
        "name_emp": "VARCHAR(255) NULL DEFAULT NULL",
        "id_reason": "INT(2) NOT NULL"
    }
    keys = "PRIMARY KEY (id_emp) USING BTREE"

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
        load_emp_reasons(None)


