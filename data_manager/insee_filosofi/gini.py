from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError

from data_manager.insee_filosofi.source import SOURCE


def get_gini(pool, geo_code, source=SOURCE):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT GI19 
                FROM insee_filosofi 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        gini = result[0]
        return float(gini) if gini is not None else None
    else:
        return None


if __name__ == '__main__':
    print(get_gini(None, "79270"))