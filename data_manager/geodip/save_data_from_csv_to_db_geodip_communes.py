import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection


def get_data_from_csv():
    def read_file(file_name, col_name):
        cols = ["zone", "value"]
        data = pd.read_csv(
            "data/2018/communes/" + file_name,
            sep=";", dtype=str, usecols=cols)
        data = data.rename(columns={"zone": "geo_code", "value": col_name})
        return data

    precariousness_fuel_nb = read_file("indicateur_precarite_tee_3d_carburant.csv", "fuel_nb")
    precariousness_fuel_prop = read_file("indicateur_precarite_tee_3d_carburant_pourcentage.csv", "fuel_prop")
    precariousness_fuel_housing_nb = read_file("indicateur_precarite_tee_3d_logement_carburant.csv", "fuel_housing_nb")
    precariousness_fuel_housing_prop = read_file("indicateur_precarite_tee_3d_logement_carburant_pourcentage.csv", "fuel_housing_prop")

    data = pd.merge(precariousness_fuel_nb, precariousness_fuel_prop, on="geo_code")
    data = pd.merge(data, precariousness_fuel_housing_prop, on="geo_code")
    data = pd.merge(data, precariousness_fuel_housing_nb, on="geo_code")

    data["fuel_prop"] = data["fuel_prop"].str.replace(",", ".")
    data["fuel_housing_prop"] = data["fuel_housing_prop"].str.replace(",", ".")

    data["geo_code"] = data["geo_code"].apply(lambda x: x.split("(")[-1].split(")")[0])
    return data



def save_data_from_csv_to_db(data):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ", date, source)"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ", CURRENT_TIMESTAMP, 'GEODIP_2018')"

    def request(cur, cols):
        cur.execute("""INSERT INTO geodip_precariousness """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    data = get_data_from_csv()
    print(data)
    print(data[data["geo_code"] == "79048"])

    # to prevent from unuseful loading data
    security = True
    if not security:
        save_data_from_csv_to_db(data)

