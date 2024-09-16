import pandas as pd
import numpy as np
import os

from data_manager.database_connection.sql_connect import mariadb_connection


def get_data_from_csv():
    variables = pd.read_csv("data/2020/dossier_complet/variables_mobin.csv", sep=";", dtype=str).dropna(subset=["COD_VAR"])
    variables["db_name"] = variables["COD_VAR"].apply(lambda x: x.replace("P20_", "").replace("C20_", ""))
    variables = variables.drop_duplicates(subset=["db_name"])
    cols = variables["COD_VAR"].dropna().tolist()

    data = pd.read_csv(
        "data/2020/dossier_complet/dossier_complet.csv",
        sep=";", dtype=str,
        usecols=["CODGEO"] + cols)
    #data.loc[:, data.columns != 'CODGEO'] = data.loc[:, data.columns != 'CODGEO'].astype("float").round()

    data = data.rename(columns=lambda name: name.replace("P20_", "").replace("C20_", ""))

    data["year_data"] = "2020"
    data["year_cog"] = "2023"

    data = data.replace({np.nan: None})
    return data, [c.replace("P20_", "").replace("C20_", "") for c in cols]


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


def load_dossier_complet_mobin(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    print(f"{table_name} - saving...")
    data, variables = get_data_from_csv()
    create_db(pool, variables, table_name)
    save_to_db(pool, data, table_name)
    print(f"{table_name} - saved...")



# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    data, variables = get_data_from_csv()

    print(data)
    print(variables)

    create_db(variables)

    # to prevent from unuseful loading data
    security = True
    if not security:
        save_to_db(data)
