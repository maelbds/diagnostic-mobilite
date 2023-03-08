import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection


def get_school_types_from_csv():
    type_cols = ["Code nature", "Nature"]
    type = pd.read_csv(
        "data/2022/fr-en-adresse-et-geolocalisation-etablissements-premier-et-second-degre.csv",
        sep=";", dtype=str,
        usecols=type_cols)
    type = type.rename(columns={"Code nature": "id_type", "Nature": "name"})
    type["id_category"] = 1
    type = type.drop_duplicates()
    type = type.sort_values(by="id_type")
    print(type)
    return type


def save_types_data_from_csv_to_db(types):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    def request(cur, cols):
        cur.execute("""INSERT INTO educationdatagouv_schools_types 
                                        (id,
                                        name,
                                        id_category
                                         ) VALUES (?,?,?)""", cols)

    [request(cur, [id_type, name, id_category])
     for id_type, name, id_category in
     zip(types["id_type"], types["name"], types["id_category"])]

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
        types = get_school_types_from_csv()
        #save_types_data_from_csv_to_db(types)
