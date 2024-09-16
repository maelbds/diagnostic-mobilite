import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.osm.work_areas_creation import create_work_areas


def get_work_areas_bdd(pool, geo_code):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT name, 
                        center_lat, 
                        center_lon, 
                        buildings_nb 
                FROM osm_work_areas 
                WHERE geo_code = ?""", [geo_code])
    result = list(cur)
    conn.close()

    work_areas = [
        [r[0], [r[1], r[2]], r[3]] for r in result
    ]
    return work_areas


def save_work_areas_bdd(pool, geo_code):
    work_areas = create_work_areas(geo_code)

    conn = mariadb_connection(pool)
    cur = conn.cursor()

    for wa in work_areas:
        name, center, buildings_nb = wa
        center_lat = center[0]
        center_lon = center[1]

        cur.execute("""INSERT INTO osm_work_areas 
                        (geo_code,
                            name, 
                            center_lat, 
                            center_lon, 
                            buildings_nb, 
                            date) VALUES (?,?,?,?,?,CURRENT_TIMESTAMP)""",
                    [geo_code,
                     name,
                     center_lat,
                     center_lon,
                     buildings_nb]
                    )

    conn.commit()
    conn.close()
    print("Work areas for commune " + str(geo_code) + " saved")
    return work_areas


def get_work_areas(pool, geo_code):
    work_areas = get_work_areas_bdd(pool, geo_code)
    if work_areas == []:
        work_areas = save_work_areas_bdd(pool, geo_code)
    return work_areas


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pprint.pprint(get_work_areas(None, 79086))
