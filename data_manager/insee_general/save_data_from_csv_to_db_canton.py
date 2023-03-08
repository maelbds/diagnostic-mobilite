"""
To load INSEE canton codes from csv to database | EXECUTE ONCE

https://www.insee.fr/fr/information/5057840
"""
import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection


def save_data_from_csv_to_db():
    """
    Read data from csv file & add it to the database
    :return:
    """
    useful_cols = ["COM", "CAN"]
    cantons = pd.read_csv("data/canton_codes.csv", sep=",", dtype="str", usecols=useful_cols)
    cantons = cantons.drop_duplicates(subset=["COM"])

    print(cantons)

    conn = mariadb_connection()
    cur = conn.cursor()

    cur.execute("""SELECT geo_code FROM insee_communes""")
    result = list(cur)
    geo_codes = [r[0] for r in result]

    to_save = pd.DataFrame(geo_codes, columns=["COM"])
    to_save = to_save.merge(cantons, on="COM", how="left").fillna(value=0)
    print(to_save)

    def request(cur, cols):
        print(cols)
        if cols[0] == 0:
            print("ok")
            cols[0] = None
        cur.execute("""UPDATE insee_communes 
                        SET canton_code = ? 
                        WHERE geo_code = ? 
                        """, cols)

    [request(cur, [canton_code, geo_code])
     for canton_code, geo_code in zip(to_save["CAN"], to_save["COM"])]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    # to prevent from unuseful loading data
    security = True
    if not security:
        save_data_from_csv_to_db()
