import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError

from data_manager.rsvero.source import SOURCE_CAR_FLEET


def get_critair(pool, geo_codes, source=SOURCE_CAR_FLEET):
    critair = {
        "critair1": {
            "label": "Crit'Air 1",
            "value": 0
        },
        "critair2": {
            "label": "Crit'Air 2",
            "value": 0
        },
        "critair3": {
            "label": "Crit'Air 3",
            "value": 0
        },
        "critair4": {
            "label": "Crit'Air 4",
            "value": 0
        },
        "critair5": {
            "label": "Crit'Air 5",
            "value": 0
        },
        "elec": {
            "label": "Electriques",
            "value": 0
        },
        "nc": {
            "label": "Non classés",
            "value": 0
        },
    }

    for geo_code in geo_codes:
        conn = mariadb_connection(pool)
        cur = conn.cursor()
        cur.execute("""SELECT critair1, critair2, critair3, critair4, critair5, electrique, non_classe 
                    FROM rsvero_critair 
                    WHERE geo_code = ? AND source = ?""", [geo_code, source])
        result = list(cur)
        conn.close()

        if len(result) > 0:
            result = result[0]
            for i in range(7):
                critair[list(critair.keys())[i]]["value"] += result[i]
            """critair = {
                "critair1": {
                    "label": "Crit'Air 1",
                    "value": result[0]
                },
                "critair2": {
                    "label": "Crit'Air 2",
                    "value": result[1]
                },
                "critair3": {
                    "label": "Crit'Air 3",
                    "value": result[2]
                },
                "critair4": {
                    "label": "Crit'Air 4",
                    "value": result[3]
                },
                "critair5": {
                    "label": "Crit'Air 5",
                    "value": result[4]
                },
                "elec": {
                    "label": "Electriques",
                    "value": result[5]
                },
                "nc": {
                    "label": "Non classés",
                    "value": result[6]
                },
            }"""
    return critair


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_critair(None, [79048, 13001]))
        pprint.pprint(get_critair(None, [13055]))
    except UnknownGeocodeError as e:
        print(e.message)
