import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection


def get_schools_from_csv():
    cols = ["Code commune", "Appellation officielle", "Code nature", "Latitude", "Longitude", "Qualité d'appariement", "Code état établissement"]
    data = pd.read_csv(
        "data/2022/fr-en-adresse-et-geolocalisation-etablissements-premier-et-second-degre.csv",
        sep=";", dtype=str,
        usecols=cols)
    data = data.rename(columns={"Code commune": "geo_code",
                                "Appellation officielle": "name",
                                "Code nature": "id_type",
                                "Latitude": "lat",
                                "Longitude": "lon",
                                "Qualité d'appariement": "quality"})
    data = data[data["Code état établissement"] == "1"]
    print(data)
    data = data[data["quality"] != "Erreur"]
    data = data.drop(columns=["Code état établissement"])
    data = data.dropna(subset=["lat", "lon"])
    print(data)
    return data


def save_data_from_csv_to_db(data):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ", source)"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ", 'EDUC_GOUV_2022')"

    def request(cur, cols):
        cur.execute("""INSERT INTO educationdatagouv_schools """ + cols_name + """ VALUES """ + values_name, cols)

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
        schools = get_schools_from_csv()
        schools = schools.replace({np.nan: None})
        print(schools)
        #save_data_from_csv_to_db(schools)
