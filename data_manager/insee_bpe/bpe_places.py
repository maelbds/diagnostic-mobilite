import pandas as pd
import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.ign.commune_center import get_coords

from data_manager.insee_bpe.source import SOURCE_BPE


def get_bpe_places(pool, geo_code, source=SOURCE_BPE):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT insee_bpe.id, insee_bpe.geo_code, insee_bpe.id_type, 
                    types.name, insee_bpe_types.name, insee_bpe_types.daily_visitors, 
                    insee_bpe_types.id_category, insee_bpe_types.characteristic, 
                    categories.name, categories.name_fr, reasons.name, reasons.name_fr, 
                    insee_bpe.lat, insee_bpe.lon, insee_bpe.quality 
                FROM insee_bpe 
                JOIN insee_bpe_types 
                ON insee_bpe.id_type = insee_bpe_types.id
                JOIN types 
                ON insee_bpe_types.id_type = types.id
                JOIN categories
                ON types.id_category = categories.id
                JOIN reasons
                ON categories.id_reason = reasons.id
                WHERE insee_bpe.geo_code = ? AND insee_bpe_types.to_keep = 1 AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    bpe_places = pd.DataFrame(result, columns=["id", "geo_code", "type_id", "type_name", "type_name_fr", "mass",
                                               "category_id", "characteristic", "category_name", "category_name_fr",
                                               "reason_name", "reason_name_fr",
                                               "lat", "lon", "quality"])

    bpe_places["type_name_fr"] = bpe_places["type_name_fr"].apply(lambda x: x.title())
    bpe_places["name"] = bpe_places["type_name_fr"]

    # Handle NaN coordinates
    lat, lon = get_coords(pool, geo_code)
    bpe_places["lat"].fillna(lat, inplace=True)
    bpe_places["lon"].fillna(lon, inplace=True)

    bpe_places = bpe_places.to_dict("records")
    return bpe_places


def get_bpe_places_no_schools(pool, geo_code, source=SOURCE_BPE):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT insee_bpe.id, insee_bpe.geo_code, insee_bpe.id_type, 
                    types.name, insee_bpe_types.name, insee_bpe_types.daily_visitors, 
                    insee_bpe_types.id_category, insee_bpe_types.characteristic, 
                    categories.name, categories.name_fr, reasons.name, reasons.name_fr, 
                    insee_bpe.lat, insee_bpe.lon, insee_bpe.quality 
                FROM insee_bpe 
                JOIN insee_bpe_types 
                ON insee_bpe.id_type = insee_bpe_types.id
                JOIN types 
                ON insee_bpe_types.id_type = types.id
                JOIN categories
                ON types.id_category = categories.id
                JOIN reasons
                ON categories.id_reason = reasons.id
                WHERE insee_bpe.geo_code = ? AND insee_bpe_types.to_keep = 1 
                AND source = ? AND categories.id != 1""", [geo_code, source])
    result = list(cur)
    conn.close()

    bpe_places = pd.DataFrame(result, columns=["id", "geo_code", "type_id", "type_name", "type_name_fr", "mass",
                                               "category_id", "characteristic", "category_name", "category_name_fr",
                                               "reason_name", "reason_name_fr",
                                               "lat", "lon", "quality"])

    bpe_places["type_name_fr"] = bpe_places["type_name_fr"].apply(lambda x: x.title())
    bpe_places["name"] = bpe_places["type_name_fr"]

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
    places = get_bpe_places(None, "79048")
    pprint.pprint([p for p in places if p["type_name"] in ["pre school", "secondary school", "primary school"]])
    print(len(places))

