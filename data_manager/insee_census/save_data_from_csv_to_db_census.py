"""
To load INSEE census data from csv to database | EXECUTE ONCE
"""
import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection

PATH = "C:/Users/maelb/Documents/2 - Travaux personnels/Transition/d - outils/0.6Planet/"


def save_data_from_csv_to_db():
    """
    Read data from csv file & add it to the database
    :return:
    """
    useful_cols = ["CANTVILLE", "NUMMI", "AGED", "COUPLE", "CS1", "DEPT", "ETUD", "ILETUD", "ILT", "INPER", "IPONDI",
                   "IRIS", "LIENF", "MOCO", "NENFR", "SEXE", "TACT", "TP", "TRANS", "TYPMR", "VOIT"]
    census = pd.read_csv(PATH + "data_manager/insee_census/data/2018/FD_INDCVI_2018.csv", sep=";", dtype="str", usecols=useful_cols)

    conn = mariadb_connection()
    cur = conn.cursor()

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_census_2018 
                                        (CANTVILLE, 
                                         NUMMI, 
                                         AGED, 
                                         COUPLE, 
                                         CS1, 
                                         DEPT, 
                                         ETUD, 
                                         ILETUD, 
                                         ILT, 
                                         INPER, 
                                         IPONDI, 
                                         IRIS, 
                                         LIENF, 
                                         MOCO, 
                                         NENFR, 
                                         SEXE, 
                                         TACT, 
                                         TP, 
                                         TRANS, 
                                         TYPMR, 
                                         VOIT) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", cols)

    [request(cur, list(row.values))
     for index, row in census.iterrows()]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    # to prevent from unuseful loading data
    security = True
    if not security:
        save_data_from_csv_to_db()
