import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError

from data_manager.insee_local.source import SOURCE_TYPMR


def get_typmr(pool, geo_code, source=SOURCE_TYPMR):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT C18_PMEN_MENPSEUL, C18_PMEN_MENSFAM, C18_PMEN_MENCOUPSENF, C18_PMEN_MENCOUPAENF, C18_PMEN_MENFAMMONO
                FROM insee_typmr 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        typmr = {
            "1": result[0],
            "2": result[1],
            "3": result[4],
            "4": result[2] + result[3],
        }
        return typmr
    else:
        return None


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_typmr(None, 79048))
        pprint.pprint(get_typmr(None, 79128))
    except UnknownGeocodeError as e:
        print(e.message)
