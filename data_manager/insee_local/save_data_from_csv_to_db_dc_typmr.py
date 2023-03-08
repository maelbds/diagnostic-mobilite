import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection


def get_data_from_csv():
    variables = pd.read_csv("data/2018/dossier_complet/variables_typmr.csv", sep=";", dtype=str)
    cols = variables["variables"].dropna().tolist()
    print(cols)

    data = pd.read_csv(
        "data/2018/dossier_complet/dossier_complet.csv",
        sep=";", dtype=str,
        usecols=cols)
    data = data.rename(columns={"CODGEO": "geo_code"})
    data.loc[:, data.columns != 'geo_code'] = data.loc[:, data.columns != 'geo_code'].astype("float").round()
    return data


def save_data_from_csv_to_db(data):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ", date, source)"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ", CURRENT_TIMESTAMP, 'INSEE_RP_2018')"

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_typmr """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

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
        typmr = get_data_from_csv()
        typmr = typmr.replace({np.nan: None})
        print(typmr)
        print(typmr[typmr["geo_code"]=="79128"])
        #save_data_from_csv_to_db(typmr)
