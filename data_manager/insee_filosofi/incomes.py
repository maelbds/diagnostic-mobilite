from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError

from data_manager.insee_filosofi.source import SOURCE


def get_median_income(pool, geo_code, source=SOURCE):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT Q219 
                FROM insee_filosofi 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        median_income = result[0]
        return int(median_income) if median_income is not None else None
    else:
        return None


if __name__ == '__main__':
    print(get_median_income(None, "79048"))