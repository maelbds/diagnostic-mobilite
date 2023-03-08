import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection


def get_bnlc_from_csv():
    # https://schema.data.gouv.fr/etalab/schema-lieux-covoiturage/latest/documentation.html#propriete-com-lieu
    cols = ["insee",
            "id_lieu", "nom_lieu",
            "type",
            "Xlong", "Ylat",
            "nbre_pl", "nbre_pmr",
            "proprio",
            "date_maj"]
    data = pd.read_csv(
        "data/bnlc/bnlc-20230216.csv",
        sep=",", dtype=str,
        usecols=cols)

    print(data)
    return data


def save_data_from_csv_to_db(data, source):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ", source)"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ", ?)"

    def request(cur, cols):
        cur.execute("""INSERT INTO transportdatagouv_bnlc """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)+[source]) for index, row in data.iterrows()]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    bnlc = get_bnlc_from_csv()

    # to prevent from unuseful loading data
    security = True
    if not security:
        bnlc = bnlc.replace({np.nan: None})
        print(bnlc)
        save_data_from_csv_to_db(bnlc, "BNLC_20230216")
