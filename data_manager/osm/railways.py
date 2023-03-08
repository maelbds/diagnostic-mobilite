import pprint
import polyline

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.osm.api_request import api_osm_request_train


def process_osm_data_way(json):
    """
    :param json: json response from api
    :return: (List) with processed data
    """
    ways = []
    for e in json:
        lat = []
        lon = []
        for p in e["geometry"]:
            lat.append(p["lat"])
            lon.append(p["lon"])
        ways.append([lat, lon])

    return ways


def get_railways_api(geo_code):
    railways = process_osm_data_way(api_osm_request_train(geo_code))
    railways_clean = []
    [railways_clean.append([[lat, lon] for lat, lon in zip(r[0], r[1])]) for r in railways]
    return railways_clean


def get_railways_bdd(pool, geo_code):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT coordinates 
                FROM osm_railways 
                WHERE geo_code = ?""", [geo_code])
    result = list(cur)
    conn.close()

    railways = [polyline.decode(r[0]) if r[0] is not None else None for r in result]
    return railways


def save_railways_bdd(pool, geo_code):
    railways = get_railways_api(geo_code)

    conn = mariadb_connection(pool)
    cur = conn.cursor()

    for r in railways:
        coordinates = polyline.encode(r)

        cur.execute("""INSERT INTO osm_railways 
                        (geo_code,
                            coordinates, 
                            date) VALUES (?,?,CURRENT_TIMESTAMP)""",
                    [geo_code,
                     coordinates]
                    )

    if len(railways) == 0:
        cur.execute("""INSERT INTO osm_railways 
                        (geo_code,
                            coordinates, 
                            date) VALUES (?,?,CURRENT_TIMESTAMP)""",
                    [geo_code,
                     None]
                    )

    conn.commit()
    conn.close()
    print("Railways for commune " + str(geo_code) + " saved")
    return railways


def get_railways(pool, geo_code):
    railways = get_railways_bdd(pool, geo_code)
    if railways == []:
        railways = save_railways_bdd(pool, geo_code)
    return railways


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np
    railways = get_railways(None, 79048)
    pprint.pprint(railways)
    for r in railways:
        r = np.array(r)
        plt.plot(r[:, 1], r[:, 0])
    plt.show()
