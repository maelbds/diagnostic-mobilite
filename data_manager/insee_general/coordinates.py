import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError, UnknownPostalcodeError


def get_coords(pool, geo_code):
    """
    Get GPS coordinates from INSEE geo code
    :param geo_code: (String) INSEE geo code
    :return: (List) [lat, lon]]
    """
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT lat, lon 
                FROM insee_communes 
                WHERE geo_code = ?""", [geo_code])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        coords = [result[0], result[1]]
        return coords
    else:
        raise UnknownGeocodeError(geo_code)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_coords(None, 79048))
    except UnknownGeocodeError as e:
        print(e.message)


