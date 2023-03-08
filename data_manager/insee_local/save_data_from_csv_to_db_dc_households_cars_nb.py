import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection


def get_cars_nb_from_csv():
    variables = pd.read_csv("data/2018/base-ccc-logement-2018/variables_cars_nb.csv", sep=";", dtype=str)
    cols = variables["variables"].dropna().tolist()
    print(cols)

    data = pd.read_csv(
        "data/2018/base-ccc-logement-2018/base-cc-logement-2018.csv",
        sep=";", dtype=str,
        usecols=cols)
    data = data.rename(columns={"CODGEO": "geo_code"})
    print(data)
    print(data[data["P18_MEN"].astype("float") < data["P18_RP_VOIT1P"].astype("float")])
    data.loc[:, data.columns != 'geo_code'] = data.loc[:, data.columns != 'geo_code'].astype("float").round()
    data["0c"] = data["P18_MEN"] - data["P18_RP_VOIT1P"]
    data = data.rename(columns={"P18_RP_VOIT1": "1c", "P18_RP_VOIT2P": "2c"})
    data.drop(columns=["P18_MEN", "P18_RP_VOIT1P"], inplace=True)
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
        cur.execute("""INSERT INTO insee_households_cars_nb """ + cols_name + """ VALUES """ + values_name, cols)

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
        cars_nb = get_cars_nb_from_csv()
        cars_nb = cars_nb.replace({np.nan: None})
        print(cars_nb)
        print(cars_nb[cars_nb["geo_code"]=="79048"])
        print(cars_nb[cars_nb["geo_code"]=="71098"])
        #save_data_from_csv_to_db(cars_nb)
