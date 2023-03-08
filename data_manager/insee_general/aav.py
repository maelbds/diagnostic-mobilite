import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError, UnknownPostalcodeError


def get_aav(pool, geo_code):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT insee_aav.code, insee_aav.name, 
                insee_aav_types.type_code, insee_aav_types.type_name, 
                insee_communes_aav_cat.cat_code, insee_communes_aav_cat.cat_name
                FROM insee_communes_aav 
                JOIN insee_aav ON insee_communes_aav.code_aav = insee_aav.code
                JOIN insee_aav_types ON insee_aav.type_code = insee_aav_types.type_code
                JOIN insee_communes_aav_cat ON insee_communes_aav.cat_commune_aav = insee_communes_aav_cat.cat_code
                WHERE geo_code = ?""", [geo_code])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        aav = {
            "code_aav": result[0],
            "name_aav": result[1],
            "type_code_aav": result[2],
            "type_name_aav": result[3],
            "type_code_commune": result[4],
            "type_name_commune": result[5]
        }
        return aav
    else:
        raise UnknownGeocodeError(geo_code)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_aav(None, "79048"))
        pprint.pprint(get_aav(None, "79191"))
        pprint.pprint(get_aav(None, "79270"))
    except UnknownGeocodeError as e:
        print(e.message)
