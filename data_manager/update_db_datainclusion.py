import pandas as pd

from data_manager.data_inclusion.save_data_inclusion import load_datainclusion
from data_manager.database_connection.sql_connect import mariadb_connection_pool


def update_db():
    pool = mariadb_connection_pool()

    print("--- updating data inclusion...")
    load_datainclusion(pool)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)
    update_db()

