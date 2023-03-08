import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError

from data_manager.insee_local.source import SOURCE_WORK_TRAVEL_MODE


def get_work_travel_mode_prop(pool, geo_code, source=SOURCE_WORK_TRAVEL_MODE):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT P18_ACTOCC15P, P18_ACTOCC15P_PASTRANS, P18_ACTOCC15P_MARCHE, P18_ACTOCC15P_VELO, P18_ACTOCC15P_2ROUESMOT, P18_ACTOCC15P_VOITURE, P18_ACTOCC15P_COMMUN 
                FROM insee_work_travel_mode 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        if result[0] != 0:
            work_travel_mode_prop = {
                "1": result[1]/result[0],
                "2": result[2]/result[0],
                "3": result[3]/result[0],
                "4": result[4]/result[0],
                "5": result[5]/result[0],
                "6": result[6]/result[0]
            }
        else:
            work_travel_mode_prop = {
                "1": 0,
                "2": 0,
                "3": 0,
                "4": 0,
                "5": 0,
                "6": 0

            }
        return work_travel_mode_prop
    else:
        return None


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_work_travel_mode_prop(None, 79048))
        pprint.pprint(get_work_travel_mode_prop(None, 59350))
    except UnknownGeocodeError as e:
        print(e.message)
