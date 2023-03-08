import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError

from data_manager.insee_local.source import SOURCE_CARS_NB


def get_households_cars_nb(pool, geo_code, source=SOURCE_CARS_NB):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT 0c, 
                          1c, 
                          2c
                FROM insee_households_cars_nb 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        households_cars_nb = {
            "0": max(result[0], 0),
            "1": result[1],
            "2": result[2]
        }
        return households_cars_nb
    else:
        return None



# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_households_cars_nb(None, 79048))
        pprint.pprint(get_households_cars_nb(None, 71098))
    except UnknownGeocodeError as e:
        print(e.message)
