import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError, UnknownPostalcodeError
from data_manager.insee_general.source import SOURCE_DENSITY


def get_density(pool, geo_code, source=SOURCE_DENSITY):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT density_code
                FROM insee_communes_density 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        density = result[0]

        return int(density)
    else:
        raise UnknownGeocodeError(geo_code)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_density(None, "79048"))
        pprint.pprint(get_density(None, "79191"))
        pprint.pprint(get_density(None, "79270"))
        print("beaujolais")
        [print(g + " - " + get_density(None, g)) for g in ['69246', '69245', '69239', '69230', '69212', '69159', '69156', '69140', '69134', '69126', '69125', '69122', '69121', '69113', '69111', '69106', '69090', '69059', '69056', '69055', '69052', '69050', '69049', '69047', '69039', '69026', '69024', '69020', '69017', '69009', '69005', '69004']]
        print("pertuis")
        [print(g + " - " + get_density(None, g)) for g in ["84089", "13059", "13074", "13048", "13099"]]
    except UnknownGeocodeError as e:
        print(e.message)
