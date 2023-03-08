import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError

from data_manager.insee_local.source import SOURCE_POP_AGE


def get_pop_age_nb(pool, geo_code, source=SOURCE_POP_AGE):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT SUM(P18_POP0002), 
                        SUM(P18_POP0305), 
                        SUM(P18_POP0610), 
                        SUM(P18_POP1117), 
                        SUM(P18_POP6579), 
                        SUM(P18_POP80P)
                FROM insee_pop_age 
                LEFT JOIN insee_arrondissements ON insee_pop_age.geo_code = insee_arrondissements.geo_code_district
                WHERE (geo_code = ? OR geo_code_city = ?) AND source = ?""", [geo_code, geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0 and result[0][0] is not None:
        result = result[0]
        pop_age_nb = {
            "-18": float(result[0]) + float(result[1]) + float(result[2]) + float(result[3]),
            "+65": float(result[4]) + float(result[5])
        }
        return pop_age_nb
    else:
        return None


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        print(get_pop_age_nb(None, 79048))
        print(get_pop_age_nb(None, 75056))
    except UnknownGeocodeError as e:
        print(e.message)
