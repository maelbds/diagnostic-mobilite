import pandas as pd
import numpy as np
from pyproj import Transformer
import time

from data_manager.database_connection.sql_connect import mariadb_connection


def get_bpe_from_csv():
    bpe_cols = ["DCIRIS", "LAMBERT_X", "LAMBERT_Y", "QUALITE_XY", "TYPEQU"]
    bpe = pd.read_csv(
        "/data_manager/insee_bpe/data/2020/bpe20_ensemble_xy.csv",
        sep=";", dtype=str,
        usecols=bpe_cols)
    bpe = bpe.astype({"LAMBERT_X": "float64", "LAMBERT_Y": "float64"})

    print(bpe)

    # Remove IRIS and keep only geocode :
    bpe["geo_code"] = bpe.apply(lambda row: row["DCIRIS"].split("_")[0], axis=1)

    print(bpe)

    # Lambert to Geodetic coordinates system :
    transformer = Transformer.from_crs("epsg:2154",  # Lambert 93
                                       "epsg:4326")  # World Geodetic System (lat/lon)
    def lambert_to_geo(x, y):
        lat, lon = transformer.transform(x, y)
        return lat, lon

    bpe[["lat", "lon"]] = bpe.apply(lambda row: lambert_to_geo(row["LAMBERT_X"], row["LAMBERT_Y"]),
                                  axis=1, result_type='expand')

    bpe = bpe.where(pd.notnull(bpe), None)
    print(bpe)
    return bpe


def save_bpe_data_from_csv_to_db(bpe):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_bpe 
                                        (geo_code,
                                        id_type,
                                        lat,
                                        lon,
                                        quality
                                         ) VALUES (?,?,?,?,?)""", cols)

    [request(cur, [geo_code, id_type, lat, lon, quality])
     for geo_code, id_type, lat, lon, quality in
     zip(bpe["geo_code"], bpe["TYPEQU"], bpe["lat"], bpe["lon"], bpe["QUALITE_XY"])]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    # to prevent from unuseful loading data
    security = True
    if not security:
        start_time = time.time()

        bpe = get_bpe_from_csv()
        save_bpe_data_from_csv_to_db(bpe)

        end_time = time.time()
        print(end_time - start_time)


