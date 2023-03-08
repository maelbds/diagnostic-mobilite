import pandas as pd
import pprint

from data_manager.database_connection.sql_connect import mariadb_connection

from data_manager.esrdatagouv.source import SOURCE_UNIVERSITIES


def get_universities(pool, geo_code, source=SOURCE_UNIVERSITIES):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT univ.id, univ.geo_code, univ_types.id_type, 
                        univ.name, 
                    types.name, univ_types.name_univ_type, univ.student_nb, 
                    types.id_category, univ_types.characteristic, 
                    categories.name, categories.name_fr, reasons.name, reasons.name_fr, 
                    univ.lat, univ.lon 
                FROM esrdatagouv_universities AS univ 
                JOIN esrdatagouv_universities_types AS univ_types
                ON univ.code_type = univ_types.id_univ_type
                JOIN types 
                ON univ_types.id_type = types.id
                JOIN categories
                ON types.id_category = categories.id
                JOIN reasons
                ON categories.id_reason = reasons.id
                WHERE univ.geo_code = ? AND univ.source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    bpe_places = pd.DataFrame(result, columns=["id", "geo_code", "type_id",
                                               "name",
                                               "type_name", "type_name_fr", "mass",
                                               "category_id", "characteristic",
                                               "category_name", "category_name_fr", "reason_name", "reason_name_fr",
                                               "lat", "lon"])

    bpe_places["mass"] = bpe_places["mass"].fillna(50)

    bpe_places = bpe_places.to_dict("records")
    return bpe_places


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.width', 1500)
    places = get_universities(None, "86194")
    print(places)
    pprint.pprint([p for p in places if p["type_name"] in ["university"]])
    print(len(places))

