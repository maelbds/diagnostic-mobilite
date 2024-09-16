import os

import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.db_functions import load_database


def get_rpc_from_csv():
    # https://schema.data.gouv.fr/etalab/schema-lieux-covoiturage/latest/documentation.html#propriete-com-lieu

    cols = {
        "journey_id": "VARCHAR(50) NOT NULL",
        "trip_id": "VARCHAR(50) NOT NULL",
        "journey_start_date": "DATE NOT NULL",
        "journey_start_lon": "FLOAT NULL DEFAULT NULL",
        "journey_start_lat": "FLOAT NULL DEFAULT NULL",
        "journey_start_insee": "VARCHAR(50) NOT NULL",
        "journey_end_date": "DATE NOT NULL",
        "journey_end_lon": "FLOAT NULL DEFAULT NULL",
        "journey_end_lat": "FLOAT NULL DEFAULT NULL",
        "journey_end_insee": "VARCHAR(50) NOT NULL",
        "passenger_seats": "INT(5) NULL DEFAULT NULL",
        "operator_class": "VARCHAR(10) NULL DEFAULT NULL",
        "journey_distance": "INT(11) NULL DEFAULT NULL",
        "journey_duration": "INT(11) NULL DEFAULT NULL",
        "has_incentive": "VARCHAR(10) NULL DEFAULT NULL",
    }
    data = pd.read_csv(
        "data/rpc/2022-12.csv",
        sep=";", dtype=str, usecols=cols.keys())

    print(data)
    return data, cols


def get_rpc_from_url(url, source, cols):
    # https://schema.data.gouv.fr/etalab/schema-lieux-covoiturage/latest/documentation.html#propriete-com-lieu
    data = pd.read_csv(url, sep=";", dtype=str,
                       usecols=[c for c in cols if c != "source"] +
                               ["journey_start_department", "journey_end_department"])
    data["source"] = source

    dep_aura = ["03", "63", "15", "43", "42", "69", "01", "38", "26", "07", "73", "74"]
    mask_departement_aura = data["journey_start_department"].isin(dep_aura) | data["journey_end_department"].isin(dep_aura)

    data = data[mask_departement_aura]
    data = data.drop(columns=["journey_start_department", "journey_end_department"])

    print(data)
    return data


def create_db(cols):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = ", ".join([col + " " + type for col, type in cols.items()]) + ","

    cur.execute("""CREATE TABLE IF NOT EXISTS mobility_raw_data.transportdatagouv_rpc 
                    (
                    """ + cols_name + """
                    year_data VARCHAR(12) NOT NULL,
                    PRIMARY KEY (journey_id) USING BTREE
                    )
                    COLLATE 'utf8_general_ci'
                    """, [])
    conn.commit()
    conn.close()


def save_to_db(data):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ")"

    def request(cur, cols):
        cur.execute("""INSERT INTO transportdatagouv_rpc """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

    conn.commit()
    conn.close()


def load_rpc(pool, table_name):
    cols_table = {
        "journey_id": "VARCHAR(50) NOT NULL",
        "trip_id": "VARCHAR(50) NOT NULL",
        "journey_start_date": "DATE NOT NULL",
        "journey_start_lon": "FLOAT NULL DEFAULT NULL",
        "journey_start_lat": "FLOAT NULL DEFAULT NULL",
        "journey_start_insee": "VARCHAR(50) NOT NULL",
        "journey_end_date": "DATE NOT NULL",
        "journey_end_lon": "FLOAT NULL DEFAULT NULL",
        "journey_end_lat": "FLOAT NULL DEFAULT NULL",
        "journey_end_insee": "VARCHAR(50) NOT NULL",
        "passenger_seats": "INT(5) NULL DEFAULT NULL",
        "operator_class": "VARCHAR(10) NULL DEFAULT NULL",
        "journey_distance": "INT(11) NULL DEFAULT NULL",
        "journey_duration": "INT(11) NULL DEFAULT NULL",
        "has_incentive": "VARCHAR(10) NULL DEFAULT NULL",

        "source": "VARCHAR(20) NOT NULL",
    }
    keys = "PRIMARY KEY (journey_id) USING BTREE, KEY (journey_start_insee) USING BTREE, KEY (journey_end_insee) USING BTREE"

    links = {
        "2022-01": "https://static.data.gouv.fr/resources/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/20220408-181757/2022-01.csv",
        "2022-02": "https://static.data.gouv.fr/resources/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/20220408-181944/2022-02.csv",
        "2022-03": "https://static.data.gouv.fr/resources/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/20220408-182230/2022-03.csv",
        "2022-04": "https://static.data.gouv.fr/resources/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/20220506-070349/2022-04.csv",
        "2022-05": "https://static.data.gouv.fr/resources/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/20220606-070318/2022-05.csv",
        "2022-06": "https://static.data.gouv.fr/resources/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/20220928-091152/2022-06.csv",
        "2022-07": "https://static.data.gouv.fr/resources/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/20220921-172646/2022-07.csv",
        "2022-08": "https://static.data.gouv.fr/resources/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/20220921-172928/2022-08.csv",
        "2022-09": "https://static.data.gouv.fr/resources/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/20221008-082134/2022-09.csv",
        "2022-10": "https://static.data.gouv.fr/resources/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/20221108-075709/2022-10.csv",
        "2022-11": "https://static.data.gouv.fr/resources/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/20221208-080530/2022-11.csv",
        "2022-12": "https://static.data.gouv.fr/resources/trajets-realises-en-covoiturage-registre-de-preuve-de-covoiturage/20230108-083037/2022-12.csv",
    }

    for source, url in links.items():
        print(f"loading rpc - {source}")
        data = get_rpc_from_url(url, source, cols_table.keys())

        load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    load_rpc(None, "test")

    rpc, cols = get_rpc_from_csv()
    rpc["source"] = "2022_12"

    print(rpc)

    # to prevent from unuseful loading data
    security = True
    if not security:
        print(rpc)
        create_db(cols)
        rpc = rpc.replace({np.nan: None})
        save_to_db(rpc)
