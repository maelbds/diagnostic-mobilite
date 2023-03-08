import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError

from data_manager.insee_local.source import SOURCE_JOBS_NB


def get_jobs_nb(pool, geo_code, source=SOURCE_JOBS_NB):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT jobs_nb 
                FROM insee_jobs_nb 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        jobs_nb = result[0]
        return jobs_nb
    else:
        return None


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_jobs_nb(None, 79048))
        pprint.pprint(get_jobs_nb(None, 13202))
    except UnknownGeocodeError as e:
        print(e.message)
