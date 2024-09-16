import pprint
import polyline

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.osm.residential_areas_creation import create_residential_areas


def get_residential_areas_bdd(pool, geo_code):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT name, 
                        center_lat, 
                        center_lon, 
                        buildings_nb, 
                        outline 
                FROM osm_residential_areas 
                WHERE geo_code = ?""", [geo_code])
    result = list(cur)
    conn.close()

    residential_areas = [
        [r[0], [r[1], r[2]], r[3], polyline.decode(r[4])] for r in result
    ]
    return residential_areas


def save_residential_areas_bdd(pool, geo_code):
    residential_areas = create_residential_areas(geo_code)

    conn = mariadb_connection(pool)
    cur = conn.cursor()

    for ra in residential_areas:
        name, center, buildings_nb, outline = ra
        center_lat = center[0]
        center_lon = center[1]
        outline = polyline.encode(outline)

        cur.execute("""INSERT INTO osm_residential_areas 
                        (geo_code,
                            name, 
                            center_lat, 
                            center_lon, 
                            buildings_nb, 
                            outline, 
                            date) VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)""",
                    [geo_code,
                     name,
                     center_lat,
                     center_lon,
                     buildings_nb,
                     outline]
                    )

    conn.commit()
    conn.close()
    print("Residential areas for commune " + str(geo_code) + " saved")
    return residential_areas


def get_residential_areas(pool, geo_code):
    residential_areas = get_residential_areas_bdd(pool, geo_code)
    if residential_areas == []:
        residential_areas = save_residential_areas_bdd(pool, geo_code)
    return residential_areas


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pprint.pprint(get_residential_areas_bdd(None, 79270))
