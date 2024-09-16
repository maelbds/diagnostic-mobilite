import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.osm.api_request import api_osm_request_center
from data_manager.osm.functions_format import process_osm_data_places

from data_manager.osm.places_types import all_places_types


def get_places_api(geo_code):
    places = []
    for z in all_places_types:
        type_id = z["id"]
        type_name = z["name"]
        osm_category = z["osm_category"]
        osm_tags = z["osm_tags"]
        print("--- get " + type_name)
        api_places = api_osm_request_center(geo_code, osm_category, osm_tags)
        light_places = process_osm_data_places(api_places, type_id)
        places += light_places
    return places


def get_places_bdd(pool, geo_code):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT osm_places.name, center_lat, center_lon, id_type, types.name, 
                categories.id, categories.name, categories.name_fr, reasons.name, reasons.name_fr
                FROM osm_places 
                LEFT JOIN types 
                ON osm_places.id_type = types.id
                LEFT JOIN categories 
                ON types.id_category = categories.id
                LEFT JOIN reasons 
                ON categories.id_reason = reasons.id
                WHERE geo_code = ?""", [geo_code])
    result = list(cur)
    conn.close()

    places = [{
                "lat": r[1],
                "lon": r[2],
                "name": r[0],
                "type_id": r[3],
                "type_name": r[4],
                "category_id": r[5],
                "category_name": r[6],
                "category_name_fr": r[7],
                "reason_name": r[8],
                "reason_name_fr": r[9]
             } for r in result]
    return places


def save_places_bdd(pool, geo_code):
    places = get_places_api(geo_code)

    conn = mariadb_connection(pool)
    cur = conn.cursor()

    for p in places:
        cur.execute("""INSERT INTO osm_places 
                        (geo_code,
                            name, 
                            center_lat, 
                            center_lon, 
                            id_type, 
                            date) VALUES (?,?,?,?,?,CURRENT_TIMESTAMP)""",
                    [geo_code,
                     p["name"],
                     p["lat"],
                     p["lon"],
                     p["type"]]
                    )

    if len(places) == 0:
        cur.execute("""INSERT INTO osm_places 
                        (geo_code,
                            name, 
                            center_lat, 
                            center_lon, 
                            id_type, 
                            date) VALUES (?,?,?,?,?,CURRENT_TIMESTAMP)""",
                    [geo_code,
                     None,
                     None,
                     None,
                     None]
                    )

    conn.commit()
    conn.close()
    print("Places for commune " + str(geo_code) + " saved")
    return places


def get_places(pool, geo_code):
    places = get_places_bdd(pool, geo_code)
    if places == []:
        save_places_bdd(pool, geo_code)
        places = get_places_bdd(pool, geo_code)

    if len(places) == 1:
        if all(v is None for v in places[0].values()):
            places = []
    return places


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pprint.pprint(get_places(None, "79048"))
