import pandas as pd
import numpy as np
import os

from data_manager.db_functions import load_database


def get_data_from_csv():
    data = pd.read_csv(
        "modes_detailed.csv",
        sep=";", decimal=",")

    data["ghg_emissions_factor"] = data["ghg_emissions_factor"].astype(float)
    data["cost_factor"] = data["cost_factor"].astype(float)

    data = data.replace({np.nan: None})

    return data


def load_modes_detailed(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    data = get_data_from_csv()

    cols_table = {
        "id": "INT(5) NOT NULL",
        "id_main_mode": "INT(5) NOT NULL",
        "name": "VARCHAR(100) NOT NULL",
        "name_fr": "VARCHAR(100) NOT NULL",
        "ghg_emissions_factor": "FLOAT NULL DEFAULT NULL",
        "ghg_emissions_factor_source": "VARCHAR(255) NULL DEFAULT NULL",
        "cost_factor": "FLOAT NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (id) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    print(get_data_from_csv())

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_modes_detailed(None, "modes_detailed")


