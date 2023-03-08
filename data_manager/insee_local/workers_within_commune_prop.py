import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError

from data_manager.insee_local.source import SOURCE_WORKERS_WITHIN_COMMUNE


def get_workers_within_commune_prop(pool, geo_code, source=SOURCE_WORKERS_WITHIN_COMMUNE):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT P18_ACTOCC15P, P18_ACTOCC15P_ILT1 
                FROM insee_workers_within_commune 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        if result[0] != 0:
            return result[1]/result[0]
        else:
            return None
    else:
        return None


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_workers_within_commune_prop(None, 79048))
        pprint.pprint(get_workers_within_commune_prop(None, 79128))
    except UnknownGeocodeError as e:
        print(e.message)
