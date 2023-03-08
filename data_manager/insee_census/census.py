import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.insee_census.prepare_census import prepare_census

from data_manager.insee_census.source import SOURCE_CENSUS


def get_census_from_cantons(pool, cantons, source=SOURCE_CENSUS):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cantons = str(cantons).replace("[", "(").replace("]", ")")

    if source == "2017":
        cur.execute("""SELECT ID,
                              IPONDI,
                              NUMMI,
                              CANTVILLE,
                              SEXE,
                              AGED,
                              CS1,
                              TACT,
                              ILT,
                              ETUD,
                              INPER,
                              NENFR,
                              TYPMR,
                              VOIT, 
                              TRANS
                    FROM insee_census_2017 
                    WHERE CANTVILLE IN """ + cantons)
    elif source == "2018":
        cur.execute("""SELECT ID,
                              IPONDI,
                              NUMMI,
                              CANTVILLE,
                              SEXE,
                              AGED,
                              CS1,
                              TACT,
                              ILT,
                              ETUD,
                              INPER,
                              NENFR,
                              TYPMR,
                              VOIT, 
                              TRANS
                    FROM insee_census_2018 
                    WHERE CANTVILLE IN """ + cantons)
    result = list(cur)
    conn.close()

    census = pd.DataFrame(result, columns=["ID",
                                           "IPONDI",
                                           "NUMMI",
                                           "CANTVILLE",
                                           "SEXE",
                                           "AGED",
                                           "CS1",
                                           "TACT",
                                           "ILT",
                                           "ETUD",
                                           "INPER",
                                           "NENFR",
                                           "TYPMR",
                                           "VOIT",
                                           "TRANS"], dtype=str)

    census = prepare_census(census)
    return census


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.width', 1500)
    census_7915 = get_census_from_cantons(None, ["7915", "7903"])
    print(census_7915)
    print(census_7915.groupby("status").count())
    print(census_7915.dtypes)
