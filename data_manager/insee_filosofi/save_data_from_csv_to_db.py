import pandas as pd
import numpy as np
from pyproj import Transformer
import time

from data_manager.database_connection.sql_connect import mariadb_connection


def get_filosofi_from_csv():
    variables = pd.read_csv("data/2019/variables.csv", sep=";", dtype=str)
    cols = variables["filosofi_2019"].dropna().tolist()
    print(cols)

    data = pd.read_csv(
        "data/2019/FILO2019_DISP_COM.csv",
        sep=";", dtype=str,
        usecols=cols)
    data = data.rename(columns={"CODGEO": "geo_code"})
    print(data)
    data = data.replace({np.nan: None})
    print(data)
    return data


def save_filosofi_from_csv_to_db(filosofi):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in filosofi.columns]) + ", date, source)"
    values_name = "(" + ", ".join(["?" for col in filosofi.columns]) + ", CURRENT_TIMESTAMP, 'FILOSOFI_2019')"

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_filosofi """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in filosofi.iterrows()]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = True
    if not security:
        filosofi = get_filosofi_from_csv()
        #save_filosofi_from_csv_to_db(filosofi)
