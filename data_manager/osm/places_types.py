import pprint

from data_manager.database_connection.sql_connect import mariadb_connection

conn = mariadb_connection()
cur = conn.cursor()
cur.execute("""SELECT types.id, types.name, categories.name 
            FROM types 
            JOIN categories 
            ON types.id_category = categories.id
            """)
result = list(cur)
conn.close()

all_places_types = [{
    "id": r[0],
    "name": r[1],
    "category": r[2],
    "osm_category": "",
    "osm_tags": []
} for r in result]


conn = mariadb_connection()
cur = conn.cursor()
cur.execute("""SELECT id_type, osm_tag, osm_category 
            FROM osm_tags 
            """)
result = list(cur)
conn.close()

for r in result:
    for zt in all_places_types:
        if r[0] == zt["id"]:
            zt["osm_category"] = r[2]
            zt["osm_tags"].append(r[1])



# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pprint.pprint(all_zone_types)

""""""
zones_list = [
    # type  category    OSM category   OSM tags
    # EDUCATION
    ["school", "education", "amenity", ["school", "kindergarten", "college", "university"]],
    # LEISURE Outing
    ["cinema", "leisure_outing", "amenity", ["cinema"]],
    ["theatre", "leisure_outing", "amenity", ["theatre"]],
    ["arts centre", "leisure_outing", "amenity", ["arts_centre"]],
    ["bowling", "leisure_outing", "amenity", ["bowlings"]],
    # LEISURE Food
    ["restaurant", "leisure_food", "amenity", ["restaurant"]],
    ["fast food", "leisure_food", "amenity", ["fast_food"]],
    ["bar", "leisure_food", "amenity", ["bar"]],
    ["cafe", "leisure_food", "amenity", ["cafe"]],
    # ACTIVITIES
    ["sport", "activities", "leisure", ["sports_center", "stadium"]],
    ["music", "activities", "amenity", ["music_school"]],
    ["community_centre", "activities", "amenity", ["community_centre"]],  # salle des fêtes
    # SHOP Food
    ["supermarket", "shop_food", "shop", ["supermarket"]],
    ["convenience store", "shop_food", "shop", ["convenience"]],
    ["bakery", "shop_food", "shop", ["bakery"]],
    ["market", "shop_food", "amenity", ["marketplace"]],
    ["focused_shops_common", "shop_food", "shop",
     ["butcher", "cheese", "greengrocer", "farm", "frozen_food", "seafood"]],
    # SHOP Goods
    ["clothes shop", "shop_goods", "shop", ["boutique", "clothes", "shoes", "second_hand"]],
    ["book store", "shop_goods", "shop", ["books"]],
    ["library", "shop_goods", "amenity", ["library"]],
    # SERVICES
    ["hairdresser", "services", "shop", ["hairdresser"]],
    ["beauty", "services", "shop", ["beauty"]],
    ["massage", "services", "shop", ["massage"]],
    # ADMINISTRATIVE
    ["bank", "administrative", "amenity", ["bank"]],
    ["post office", "administrative", "amenity", ["post_office"]],
    ["townhall", "administrative", "amenity", ["townhall"]],
    # MEDICAL Common
    ["pharmacy", "medical_common", "amenity", ["pharmacy"]],
    ["doctor", "medical_common", "amenity", ["doctors"]],
    # MEDICAL Exceptional
    ["dentist", "medical_exceptional", "amenity", ["dentist"]],
    ["clinic", "medical_exceptional", "amenity", ["clinic"]],
    ["hospital", "medical_exceptional", "amenity", ["hospital"]],
    # INFRASTRUCTURES
    ["railway station", "infrastructures", "railway", ["station"]]
]

