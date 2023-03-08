import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError


def geo_code_to_canton_code(pool, geo_code):
    """
    Convert INSEE geo code to canton code
    :param geo_code: (String) INSEE geo code
    :return: (String) Canton code
    """
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT canton_code 
                FROM insee_communes 
                WHERE geo_code = ?""", [geo_code])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        canton_code = result[0]
        return canton_code
    else:
        raise UnknownGeocodeError(geo_code)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(geo_code_to_canton_code(None, 79048))
    except UnknownGeocodeError as e:
        print(e.message)


