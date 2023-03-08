import pandas as pd
import numpy as np
from pyproj import Transformer
import time

from data_manager.database_connection.sql_connect import mariadb_connection


def get_cog_communes_from_csv():
    cols = ["TYPECOM", "COM", "DEP", "REG", "CAN", "ARR", "NCCENR", "LIBELLE", "COMPARENT"]
    data = pd.read_csv(
        "data/2022/commune_2022.csv",
        sep=",", dtype=str,
        usecols=cols)

    data = data[(data["TYPECOM"]=="COM") | (data["TYPECOM"]=="ARM")] # to remove former communes
    data.drop(columns=["TYPECOM"], inplace=True)

    data = data.replace({np.nan: None})
    return data


def save_cog_communes_to_db(cog):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in cog.columns]) + ", year)"
    values_name = "(" + ", ".join(["?" for col in cog.columns]) + ", '2022')"

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_cog_communes """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in cog.iterrows()]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    cog_communes = get_cog_communes_from_csv()
    print(cog_communes)

    # to prevent from unuseful loading data
    security = True
    if not security:
        save_cog_communes_to_db(cog_communes)
