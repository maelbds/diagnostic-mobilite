import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection


def get_places_categories():
    conn = mariadb_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT * 
            FROM categories""")
    result = list(cur)
    places_categories = pd.DataFrame(result, columns=["id", "name", "name_fr", "id_reason", "characteristic_level_0",
                                               "characteristic_level_1", "characteristic_level_2"]
                              ).set_index("id")
    conn.close()
    return places_categories


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)
    places_categories = get_places_categories()
    print(places_categories)


