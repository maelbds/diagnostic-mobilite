import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError
from data_manager.insee_local.source import SOURCE_POPULATION


def get_population_bdd(pool, geo_code, source):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT P18_POP 
                FROM insee_population 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        pop = result[0]
        return pop
    else:
        return None


def get_population(pool, geo_code, source=SOURCE_POPULATION):
    population = get_population_bdd(pool, geo_code, source)
    return population


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_population(None, "13202"))
    except UnknownGeocodeError as e:
        print(e.message)
