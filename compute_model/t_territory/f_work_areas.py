import pandas as pd
import numpy as np
from pyproj import Transformer

from compute_model.v_database_connection.db_request import db_request
from compute_model.sources import sources


def get_work_areas(geo_codes):
    result = db_request(
        """ SELECT dc.CODGEO, dc.EMPLT, 
                   ign.chflieu_lat, ign.chflieu_lon,
                   ign.centroid_lat, ign.centroid_lon,
                   sur.surface
            FROM insee_dossier_complet AS dc
            LEFT JOIN ign_commune_center AS ign ON dc.CODGEO = ign.geo_code
            LEFT JOIN ign_commune_surface AS sur ON dc.CODGEO = sur.geo_code
            WHERE dc.CODGEO IN :geo_codes AND dc.year_data = :year_data
        """,
        {
            "geo_codes": geo_codes,
            "year_data": sources["dossier_complet"]["year"]
        }
    )
    work_com = pd.DataFrame(result, columns=["geo_code", "nb_empl",
                                             "chflieu_lat", "chflieu_lon",
                                             "centroid_lat", "centroid_lon",
                                             "surface"])

    mask_no_chflieu = work_com["chflieu_lat"].isna() | work_com["chflieu_lon"].isna()
    work_com.loc[mask_no_chflieu, "chflieu_lat"] = work_com.loc[mask_no_chflieu, "centroid_lat"]
    work_com.loc[mask_no_chflieu, "chflieu_lon"] = work_com.loc[mask_no_chflieu, "centroid_lon"]

    work_com["inner_dist"] = [round(np.sqrt(float(s)), 1) * 1000 if s is not None else 1000 for s in work_com["surface"]]

    # Geo to Lambert93 coordinates system :
    transformer2154 = Transformer.from_crs("epsg:4326",  # World Geodetic System (lat/lon)
                                           "epsg:2154")  # Lambert 93 (x, y)

    def geo_to_lambert(lat, lon):
        x, y = transformer2154.transform(lat, lon)
        return [round(x), round(y)]

    work_com["coords_geo"] = [[lat, lon]for lat, lon in zip(work_com["chflieu_lat"], work_com["chflieu_lon"])]
    work_com["coords_lamb"] = [geo_to_lambert(lat, lon) for lat, lon in zip(work_com["chflieu_lat"], work_com["chflieu_lon"])]

    work_com.drop(columns=["chflieu_lat", "chflieu_lon", "centroid_lat", "centroid_lon", "surface"], inplace=True)
    work_com["id"] = work_com.index
    work_com["id"] = "wa_" + work_com["id"].astype(str)
    work_com["category"] = "work"
    work_com["reason"] = "work"
    work_com.rename(columns={"nb_empl": "mass"}, inplace=True)

    work_com = work_com[["id", "geo_code", "mass", "coords_geo", "coords_lamb", "inner_dist", "category", "reason"]]

    return work_com


if __name__ == '__main__':
    print(get_work_areas(["79048", "79191"]))
