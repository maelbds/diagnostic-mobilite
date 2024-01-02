import pandas as pd
import numpy as np

from compute_model.v_database_connection.db_request import save_to_db, db_request
from data_manager.db_functions import load_database


def create_table_travels(pool, table_name):
    cols_table = {
        "id_ind": "VARCHAR(50) NOT NULL",
        "id_trav": "VARCHAR(50) NOT NULL",
        "trav_nb": "INT(3) NULL DEFAULT NULL",
        "w_trav": "FLOAT NOT NULL",
        "geo_code": "VARCHAR(10) NOT NULL",
        "mode": "VARCHAR(10) NOT NULL",
        "reason_ori": "VARCHAR(10) NOT NULL",
        "reason_des": "VARCHAR(10) NOT NULL",
        "distance": "FLOAT NOT NULL",
        "geo_code_ori": "VARCHAR(10) NULL DEFAULT NULL",
        "geo_code_des": "VARCHAR(10) NULL DEFAULT NULL",
        "nb_passengers": "INT(2) NULL DEFAULT NULL",
        "source_id": "VARCHAR(50) NOT NULL",
        "distance_emp": "FLOAT NOT NULL",
    }

    keys = "PRIMARY KEY (id_trav) USING BTREE, KEY (geo_code) USING BTREE"

    data = pd.DataFrame(columns=cols_table.keys())

    load_database(pool, table_name, data, cols_table, keys)


def create_table_travels_analysis(pool, table_name):
    cols_table = {
        "siren": "VARCHAR(50) NOT NULL",
        "nb_car": "FLOAT NULL DEFAULT NULL",
        "nb_car_pass": "FLOAT NULL DEFAULT NULL",
        "nb_pt": "FLOAT NULL DEFAULT NULL",
        "nb_bike": "FLOAT NULL DEFAULT NULL",
        "nb_pedestrian": "FLOAT NULL DEFAULT NULL",
        "dist_car": "FLOAT NULL DEFAULT NULL",
        "dist_car_pass": "FLOAT NULL DEFAULT NULL",
        "dist_pt": "FLOAT NULL DEFAULT NULL",
        "dist_bike": "FLOAT NULL DEFAULT NULL",
        "dist_pedestrian": "FLOAT NULL DEFAULT NULL",
        "avg_dist": "FLOAT NULL DEFAULT NULL",
    }

    keys = "PRIMARY KEY (siren) USING BTREE"

    data = pd.DataFrame(columns=cols_table.keys())

    load_database(pool, table_name, data, cols_table, keys)


def save_travels(travels):
    travels = travels.replace({np.nan: None})
    save_to_db(None, travels, "computed_travels")
    return


def save_travels_analysis(siren, analysis):
    analysis["siren"] = siren
    analysis = analysis.replace({np.nan: None})
    save_to_db(None, analysis, "computed_travels_analysis")
    return


def get_saved_travels_siren():
    result = db_request(
        """ SELECT siren
            FROM computed_travels_analysis
        """,
        {}
    )
    travels = pd.DataFrame(result, columns=["siren"])
    return travels["siren"].drop_duplicates().to_list()


if __name__ == '__main__':
    create_table_travels(None, "computed_travels")
    create_table_travels_analysis(None, "computed_travels_analysis")

