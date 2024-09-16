import pandas as pd

from data_manager.emd.compute_and_save_mobloc import load_emd_mobloc
from data_manager.emd.compute_and_save_perimeter import load_emd_perimeter
from data_manager.emd.data.montpellier.read_emd import read_emd_montpellier

from data_manager.db_functions import load_database
from data_manager.emd.save_data_from_csv_to_db_modes import load_emd_modes
from data_manager.emd.save_data_from_csv_to_db_reasons import load_emd_reasons


def load_dataset(pool, dataset):
    table_name = "emd_datasets"
    cols_table = {
        "emd_id": "VARCHAR(50) NOT NULL",
        "emd_name": "VARCHAR(255) NOT NULL",
        "emd_link": "VARCHAR(255) NULL DEFAULT NULL",
        "emd_year": "VARCHAR(5) NULL DEFAULT NULL"
    }
    keys = "PRIMARY KEY (emd_id) USING BTREE"

    load_database(pool, table_name, dataset, cols_table, keys)


def load_persons(pool, persons):
    table_name = "emd_persons"
    cols_table = {
        "emd_id": "VARCHAR(50) NOT NULL",
        "id_ind": "VARCHAR(50) NOT NULL",
        "id_hh": "VARCHAR(50) NULL DEFAULT NULL",
        "w_ind": "FLOAT NULL DEFAULT NULL",
        "ra_id": "VARCHAR(50) NULL DEFAULT NULL",
        "ech": "INT(5) NULL DEFAULT NULL",
        "per": "INT(2) NULL DEFAULT NULL",
        "sexe": "INT(2) NULL DEFAULT NULL",
        "age": "INT(3) NULL DEFAULT NULL",
        "status": "VARCHAR(50) NULL DEFAULT NULL",
        "csp": "INT(2) NULL DEFAULT NULL",
        "nb_car": "INT(2) NULL DEFAULT NULL",
        "day": "INT(2) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (emd_id, id_ind) USING BTREE"

    load_database(pool, table_name, persons, cols_table, keys)


def load_travels(pool, travels):
    table_name = "emd_travels"
    cols_table = {
        "emd_id": "VARCHAR(50) NOT NULL",
        "id_trav": "VARCHAR(50) NOT NULL",
        "id_ind": "VARCHAR(50) NOT NULL",
        "ra_id": "VARCHAR(50) NOT NULL",
        "ech": "INT(5) NULL DEFAULT NULL",
        "per": "INT(2) NULL DEFAULT NULL",
        "trav_nb": "INT(2) NULL DEFAULT NULL",
        "reason_ori": "VARCHAR(10) NULL DEFAULT NULL",
        "zone_ori": "VARCHAR(10) NULL DEFAULT NULL",
        "hour_ori": "VARCHAR(10) NULL DEFAULT NULL",
        "reason_des": "VARCHAR(10) NULL DEFAULT NULL",
        "zone_des": "VARCHAR(10) NULL DEFAULT NULL",
        "hour_des": "VARCHAR(10) NULL DEFAULT NULL",
        "duration": "INT(5) NULL DEFAULT NULL",
        "modp": "VARCHAR(10) NULL DEFAULT NULL",
        "moip": "VARCHAR(10) NULL DEFAULT NULL",
        "distance": "VARCHAR(50) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (emd_id, id_trav) USING BTREE, KEY (id_ind) USING BTREE"

    load_database(pool, table_name, travels, cols_table, keys)


def load_modes_dict(pool, modes_dict):
    table_name = "emd_modes_dict"
    cols_table = {
        "emd_id": "VARCHAR(50) NOT NULL",
        "value": "VARCHAR(50) NOT NULL",
        "description": "VARCHAR(255) NULL DEFAULT NULL",
        "mode_id": "INT(5) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (emd_id, value) USING BTREE, KEY (mode_id) USING BTREE"

    load_database(pool, table_name, modes_dict, cols_table, keys)


def load_reasons_dict(pool, reasons_dict):
    table_name = "emd_reasons_dict"
    cols_table = {
        "emd_id": "VARCHAR(50) NOT NULL",
        "value": "VARCHAR(50) NOT NULL",
        "description": "VARCHAR(255) NULL DEFAULT NULL",
        "reason_id": "INT(5) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (emd_id, value) USING BTREE, KEY (reason_id) USING BTREE"

    load_database(pool, table_name, reasons_dict, cols_table, keys)


def load_geo(pool, geo):
    table_name = "emd_geo"
    cols_table = {
        "emd_id": "VARCHAR(50) NOT NULL",
        "id": "VARCHAR(50) NOT NULL",
        "name": "VARCHAR(255) NULL DEFAULT NULL",
        "geo_code": "VARCHAR(50) NULL DEFAULT NULL",
        "geometry": "GEOMETRYCOLLECTION NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (emd_id, id) USING BTREE, KEY (geo_code) USING BTREE"

    load_database(pool, table_name, geo, cols_table, keys)


def load_emd(pool):
    load_emd_modes(pool)
    load_emd_reasons(pool)

    all_emd_funcs = [
        read_emd_montpellier
    ]

    for emd_func in all_emd_funcs:
        emd_id, dataset, persons, travels, modes_dict, reasons_dict, geo = emd_func(pool)

        load_dataset(pool, dataset)
        load_persons(pool, persons)
        load_travels(pool, travels)
        load_modes_dict(pool, modes_dict)
        load_reasons_dict(pool, reasons_dict)
        load_geo(pool, geo)

        load_emd_mobloc(pool, emd_id)
        load_emd_perimeter(pool, emd_id)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 65)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    security = False
    if not security:
        load_emd(None)

