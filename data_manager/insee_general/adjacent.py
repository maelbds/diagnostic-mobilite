from data_manager.database_connection.sql_connect import mariadb_connection

from data_manager.insee_general.source import SOURCE_ADJACENT


def get_adjacent(pool, geo_code, source=SOURCE_ADJACENT):
    """
    Convert INSEE geo code to postal code
    :param geo_code: (String) INSEE geo code
    :return: (String) Postal code
    """
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT geo_code_neighbor 
                FROM osm_adjacent 
                WHERE geo_code = ? AND SOURCE = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        return [r[0] for r in result]
    else:
        return []

# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    print(get_adjacent(None, 79048))

