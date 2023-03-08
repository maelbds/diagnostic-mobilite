import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError

from data_manager.insee_local.source import SOURCE_TOPOGRAPHY


def get_surface(pool, geo_code, source=SOURCE_TOPOGRAPHY):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT surface 
                FROM insee_topography 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        surface = result[0]
        return float(surface) if surface is not None else None
    else:
        return None


def get_artificialization_rate(pool, geo_code, source=SOURCE_TOPOGRAPHY):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT artificialization_rate 
                FROM insee_topography 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        artificialization_rate = result[0]
        return float(artificialization_rate) if artificialization_rate is not None else None
    else:
        return None


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_artificialization_rate(None, 79048))
        pprint.pprint(get_surface(None, 79048))
    except UnknownGeocodeError as e:
        print(e.message)
