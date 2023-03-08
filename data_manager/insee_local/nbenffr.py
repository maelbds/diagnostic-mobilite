import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError

from data_manager.insee_local.source import SOURCE_NBENFFR


def get_nbenffr(pool, geo_code, source=SOURCE_NBENFFR):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT C18_NE24F0, C18_NE24F1, C18_NE24F2, C18_NE24F3, C18_NE24F4P
                FROM insee_nbenffr 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        nbenffr = {
            0: result[0],
            1: result[1],
            2: result[2],
            3: result[3],
            4: result[4]
        }
        return nbenffr
    else:
        return None



# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        g_code = 79048
        nb_enf = get_nbenffr(None, g_code)
        pprint.pprint(nb_enf)
        g_code = 79128
        nb_enf = get_nbenffr(None, g_code)
        pprint.pprint(nb_enf)
    except UnknownGeocodeError as e:
        print(e.message)
