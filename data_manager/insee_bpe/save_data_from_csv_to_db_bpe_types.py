import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection


def get_bpe_types_from_csv():
    bpe_type_cols = ["CODE", "DESCRIPTION", "CATEGORIE", "DAILY_VISITORS", "TO_KEEP"]
    bpe_type = pd.read_csv(
        "/data_manager/insee_bpe/data/2020/types_categories.csv",
        sep=";", dtype=str,
        usecols=bpe_type_cols)
    bpe_type = bpe_type.astype({"CATEGORIE": "int32", "DAILY_VISITORS": "int32"})

    print(bpe_type)
    return bpe_type


def save_bpe_types_data_from_csv_to_db(bpe):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_bpe_types 
                                        (id_type,
                                        name,
                                        id_category,
                                        daily_visitors,
                                        to_keep
                                         ) VALUES (?,?,?,?, ?)""", cols)

    [request(cur, [id_type, name, id_category, daily_visitors, to_keep])
     for id_type, name, id_category, daily_visitors, to_keep in
     zip(bpe["CODE"], bpe["DESCRIPTION"], bpe["CATEGORIE"], bpe["DAILY_VISITORS"], bpe["TO_KEEP"])]

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
        bpe_types = get_bpe_types_from_csv()
        save_bpe_types_data_from_csv_to_db(bpe_types)


