"""
To load INSEE census data from csv to database | EXECUTE ONCE
"""
import pandas as pd
import os
import numpy as np


from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.insee_census.prepare_census import prepare_census
from data_manager.utilities import load_file


def download_files():
    # reference : "https://www.insee.fr/fr/statistiques/5542859?sommaire=5395764"

    files = [{
        "name": "INSEE Census 2018 - COG 2020",
        "url": "https://www.insee.fr/fr/statistiques/fichier/5542859/RP2018_INDCVI_csv.zip",
        "dir": "data/2018",
        "zip_name": "census2018.zip",
        "file_name": "FD_INDCVI_2018.csv",
    }]

    [load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def get_data_from_csv_and_save_to_db(pool, table_name):
    cols = ["CANTVILLE", "NUMMI", "AGED", "COUPLE", "CS1", "DEPT", "ETUD", "ILETUD", "ILT", "INPER", "IPONDI",
                   "IRIS", "LIENF", "MOCO", "NENFR", "SEXE", "TACT", "TP", "TRANS", "TYPMR", "VOIT"]
    cols = {col: "VARCHAR(50)" for col in cols}

    data = pd.read_csv("data/2018/FD_INDCVI_2018.csv", sep=";", dtype=str, usecols=cols)  # , nrows=10000)

    batch = 1000000
    total = len(data)
    for i in range(int(np.ceil(total/batch))):
        print(f"-- batch {i}")
        data_batch = data.iloc[i * batch: (i + 1) * batch]
        data_batch, added_cols = prepare_census(data_batch)
        cols.update(added_cols)

        data_batch["year_data"] = "2018"
        data_batch["year_cog"] = "2021"
        data_batch = data_batch.replace({np.nan: None})

        create_db(pool, cols, table_name)
        save_to_db(pool, data_batch, table_name)
        print("--saved")

    return data, cols


def create_db(pool, cols, table_name):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    cols_name = ", ".join([f"{col} {type} NULL DEFAULT NULL" for col, type in cols.items()]) + ","

    cur.execute("""CREATE TABLE IF NOT EXISTS """ + table_name + """ 
                    (
                    id INT(11) NOT NULL AUTO_INCREMENT,
                    """ + cols_name + """
                    year_data VARCHAR(12) NOT NULL,
                    year_cog VARCHAR(12) NOT NULL,
                    PRIMARY KEY (id, year_data) USING BTREE, KEY (CANTVILLE) USING BTREE
                    )
                    COLLATE 'utf8_general_ci'
                    """, [])
    conn.commit()
    conn.close()


def save_to_db(pool, data, table_name):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ")"

    def request(cur, cols):
        cur.execute("INSERT INTO " + table_name + " " + cols_name + " VALUES " + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

    conn.commit()
    conn.close()


def load_census(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    print(f"{table_name} - saving...")
    data = get_data_from_csv_and_save_to_db(pool, table_name)
    print(f"{table_name} - saved...")


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_census(None, "insee_census")
