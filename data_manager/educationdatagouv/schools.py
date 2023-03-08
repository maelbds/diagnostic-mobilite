import pandas as pd
import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.ign.commune_center import get_coords

from data_manager.educationdatagouv.source import SOURCE_SCHOOLS


def get_schools(pool, geo_code, source=SOURCE_SCHOOLS):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT educationdatagouv_schools.id, educationdatagouv_schools.geo_code, educationdatagouv_schools.id_type, 
                        educationdatagouv_schools.name, 
                    types.name, educationdatagouv_schools_types.name, educationdatagouv_schools_types.daily_visitors, 
                    educationdatagouv_schools_types.id_category, educationdatagouv_schools_types.characteristic, 
                    categories.name, categories.name_fr, reasons.name, reasons.name_fr, 
                    educationdatagouv_schools.lat, educationdatagouv_schools.lon, educationdatagouv_schools.quality 
                FROM educationdatagouv_schools 
                JOIN educationdatagouv_schools_types 
                ON educationdatagouv_schools.id_type = educationdatagouv_schools_types.id
                JOIN types 
                ON educationdatagouv_schools_types.id_type = types.id
                JOIN categories
                ON types.id_category = categories.id
                JOIN reasons
                ON categories.id_reason = reasons.id
                WHERE educationdatagouv_schools.geo_code = ? AND educationdatagouv_schools_types.to_keep = 1 AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    bpe_places = pd.DataFrame(result, columns=["id", "geo_code", "type_id",
                                               "name",
                                               "type_name", "type_name_fr", "mass",
                                               "category_id", "characteristic",
                                               "category_name", "category_name_fr", "reason_name", "reason_name_fr",
                                               "lat", "lon", "quality"])

    bpe_places["type_name_fr"] = bpe_places["type_name_fr"].apply(lambda x: x.title())

    # Handle NaN coordinates
    lat, lon = get_coords(pool, geo_code)
    bpe_places["lat"].fillna(lat, inplace=True)
    bpe_places["lon"].fillna(lon, inplace=True)

    bpe_places = bpe_places.to_dict("records")
    return bpe_places


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.width', 1500)
    places = get_schools(None, "79048")
    print(places)
    pprint.pprint([p for p in places if p["type_name"] in ["pre school", "secondary school", "primary school"]])
    print(len(places))

