import pandas as pd

from data_manager.db_functions import load_database


def create_table_datasets(pool, table_name):
    cols_table = {
        "datagouv_id": "VARCHAR(50) NOT NULL",
        "name": "VARCHAR(250) NULL DEFAULT NULL",
        "file_name": "VARCHAR(250) NULL DEFAULT NULL",
        "url": "VARCHAR(250) NULL DEFAULT NULL",
        "end_calendar_validity": "DATE NULL DEFAULT NULL",
        "saved_on": "DATETIME NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (datagouv_id) USING BTREE"

    data = pd.DataFrame(columns=cols_table.keys())

    load_database(pool, table_name, data, cols_table, keys)


def create_table_agency(pool, table_name):
    cols_table = {
        "datagouv_id": "VARCHAR(50) NOT NULL",
        "agency_id": "VARCHAR(200) NOT NULL",
        "agency_name": "VARCHAR(200) NULL DEFAULT NULL",
        "saved_on": "DATETIME NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (datagouv_id, agency_id) USING BTREE"

    data = pd.DataFrame(columns=cols_table.keys())

    load_database(pool, table_name, data, cols_table, keys)


def create_table_calendar(pool, table_name):
    cols_table = {
        "datagouv_id": "VARCHAR(50) NOT NULL",
        "service_id": "VARCHAR(200) NOT NULL",
        "monday": "TINYINT(4) NULL DEFAULT NULL",
        "tuesday": "TINYINT(4) NULL DEFAULT NULL",
        "wednesday": "TINYINT(4) NULL DEFAULT NULL",
        "thursday": "TINYINT(4) NULL DEFAULT NULL",
        "friday": "TINYINT(4) NULL DEFAULT NULL",
        "saturday": "TINYINT(4) NULL DEFAULT NULL",
        "sunday": "TINYINT(4) NULL DEFAULT NULL",
        "start_date": "DATE NULL DEFAULT NULL",
        "end_date": "DATE NULL DEFAULT NULL",
        "saved_on": "DATETIME NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (datagouv_id, service_id) USING BTREE"

    data = pd.DataFrame(columns=cols_table.keys())

    load_database(pool, table_name, data, cols_table, keys)


def create_table_geocodes(pool, table_name):
    cols_table = {
        "geo_code": "VARCHAR(50) NOT NULL",
        "datagouv_id": "VARCHAR(50) NOT NULL",
        "route_id": "VARCHAR(200) NOT NULL",
        "main_trip_id": "VARCHAR(200) NOT NULL"
    }
    keys = "PRIMARY KEY (geo_code, datagouv_id, route_id, main_trip_id) USING BTREE"

    data = pd.DataFrame(columns=cols_table.keys())

    load_database(pool, table_name, data, cols_table, keys)


def create_table_routes(pool, table_name):
    cols_table = {
        "datagouv_id": "VARCHAR(50) NOT NULL",
        "route_id": "VARCHAR(200) NOT NULL",
        "agency_id": "VARCHAR(200) NULL DEFAULT NULL",
        "route_short_name": "VARCHAR(250) NULL DEFAULT NULL",
        "route_long_name": "VARCHAR(300) NULL DEFAULT NULL",
        "route_type": "INT(11) NULL DEFAULT NULL",
        "saved_on": "DATETIME NULL DEFAULT NULL"
    }
    keys = "PRIMARY KEY (datagouv_id, route_id) USING BTREE"

    data = pd.DataFrame(columns=cols_table.keys())

    load_database(pool, table_name, data, cols_table, keys)


def create_table_stops(pool, table_name):
    cols_table = {
        "datagouv_id": "VARCHAR(50) NOT NULL",
        "stop_id": "VARCHAR(100) NOT NULL",
        "stop_name": "VARCHAR(250) NULL DEFAULT NULL",
        "stop_lat": "FLOAT NULL DEFAULT NULL",
        "stop_lon": "FLOAT NULL DEFAULT NULL",
        "saved_on": "DATETIME NULL DEFAULT NULL"
    }
    keys = "PRIMARY KEY (datagouv_id, stop_id) USING BTREE"

    data = pd.DataFrame(columns=cols_table.keys())

    load_database(pool, table_name, data, cols_table, keys)


def create_table_stop_times(pool, table_name):
    cols_table = {
        "datagouv_id": "VARCHAR(50) NOT NULL",
        "trip_id": "VARCHAR(150) NOT NULL",
        "stop_id": "VARCHAR(100) NOT NULL",
        "arrival_time": "TIME NULL DEFAULT NULL",
        "departure_time": "TIME NULL DEFAULT NULL",
        "stop_sequence": "INT(11) NOT NULL",
        "saved_on": "DATETIME NULL DEFAULT NULL"
    }
    keys = "PRIMARY KEY (datagouv_id, trip_id, stop_id, stop_sequence) USING BTREE"

    data = pd.DataFrame(columns=cols_table.keys())

    load_database(pool, table_name, data, cols_table, keys)


def create_table_trips(pool, table_name):
    cols_table = {
        "datagouv_id": "VARCHAR(50) NOT NULL",
        "trip_id": "VARCHAR(150) NOT NULL",
        "route_id": "VARCHAR(200) NULL DEFAULT NULL",
        "service_id": "VARCHAR(200) NULL DEFAULT NULL",
        "saved_on": "DATETIME NULL DEFAULT NULL"
    }
    keys = "PRIMARY KEY (datagouv_id, trip_id) USING BTREE, KEY (route_id) USING BTREE"

    data = pd.DataFrame(columns=cols_table.keys())

    load_database(pool, table_name, data, cols_table, keys)
