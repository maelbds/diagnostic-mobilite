import pandas as pd
import numpy as np
import os

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.utilities import load_file


def download_files():
    # reference : "https://www.insee.fr/fr/statistiques/5359146#consulter"

    files = [{
        "name": "Dossier complet 2018 - COG 2021",
        "url": "https://diagnostic-mobilite.fr/data/2018/dossier_complet.zip", # not available anymore on INSEE website
        "dir": "data/2018",
        "zip_name": "dossier_complet2018.zip",
        "file_name": "dossier_complet.csv",
    }]

    [load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def get_data_from_csv():
    variables = pd.read_csv("data/2018/variables_dossier_complet.csv", sep=";", dtype=str)
    cols = variables["variables"].dropna().drop_duplicates().tolist()

    data = pd.read_csv(
        "data/2018/dossier_complet.csv",
        sep=";", dtype=str,
        usecols=cols)
    data.loc[:, data.columns != 'CODGEO'] = data.loc[:, data.columns != 'CODGEO'].astype("float").round()

    data = data.rename(columns=lambda name: name.replace("P18_", "").replace("C18_", ""))
    cols = data.columns.tolist()
    cols.remove("CODGEO")

    data["year_data"] = "2018"
    data["year_cog"] = "2021"

    data = data.replace({np.nan: None})
    return data, cols


def create_db(pool, cols, table_name):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    cols_name = ", ".join([col + " INT(11) NULL DEFAULT NULL" for col in cols]) + ","

    cur.execute("""CREATE TABLE IF NOT EXISTS """ + table_name + """ 
                    (
                    CODGEO VARCHAR(12) NOT NULL,
                    """ + cols_name + """
                    year_data VARCHAR(12) NOT NULL,
                    year_cog VARCHAR(12) NOT NULL,
                    PRIMARY KEY (CODGEO, year_data) USING BTREE
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


def load_dossier_complet(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    print(f"{table_name} - saving...")
    data, cols = get_data_from_csv()
    create_db(pool, cols, table_name)
    save_to_db(pool, data, table_name)
    print(f"{table_name} - saved...")



# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    data, cols = get_data_from_csv()

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_dossier_complet(None, "insee_dossier_complet")
