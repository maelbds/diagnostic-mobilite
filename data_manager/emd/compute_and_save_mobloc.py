import pandas as pd

from compute_model.database_connection.db_request import db_request
from shapely import centroid, from_wkb, distance, Point
from shapely.ops import transform

from pyproj import Transformer

from data_manager.db_functions import load_database


def compute_mobloc(emd_id):
    result = db_request(
        """SELECT  t.emd_id, t.id_trav, 
        
                   t.ra_id, t.zone_ori, t.zone_des,

                   emd_geo_res.geometry,
                   emd_geo_ori.geometry, 
                   emd_geo_des.geometry,
                   
                   distance

           FROM emd_travels AS t

           LEFT JOIN emd_geo AS emd_geo_ori ON t.zone_ori = emd_geo_ori.id AND t.emd_id = emd_geo_ori.emd_id
           LEFT JOIN emd_geo AS emd_geo_des ON t.zone_des = emd_geo_des.id AND t.emd_id = emd_geo_des.emd_id
           LEFT JOIN emd_geo AS emd_geo_res ON t.ra_id = emd_geo_res.id AND t.emd_id = emd_geo_res.emd_id

           WHERE t.emd_id = :emd_id 
        """,
        {
            "emd_id": emd_id
        })

    travels = pd.DataFrame(result, columns=["emd_id", "id_trav",
                                            "ra_id", "ori_id", "des_id",
                                            "res_geo", "ori_geo", "des_geo", "distance"])

    # Geo to Lambert93 coordinates system :
    transformer2154 = Transformer.from_crs("epsg:4326",  # Système Inspire
                                           "epsg:2154",  # Lambert 93 (x, y)
                                           always_xy=True)

    def wkb_to_geojson(wkb_geom):
        return from_wkb(wkb_geom)

    def geo_to_center_lamb(geo):
        center = centroid(geo)
        center_lamb = transform(transformer2154.transform, center) if center is not None else Point(0, 0)
        return center_lamb

    travels["res_geo"] = travels["res_geo"].apply(lambda geo: wkb_to_geojson(geo))
    travels["ori_geo"] = travels["ori_geo"].apply(lambda geo: wkb_to_geojson(geo))
    travels["des_geo"] = travels["des_geo"].apply(lambda geo: wkb_to_geojson(geo))

    travels["res_center"] = travels["res_geo"].apply(lambda geo: geo_to_center_lamb(geo))
    travels["ori_center"] = travels["ori_geo"].apply(lambda geo: geo_to_center_lamb(geo))
    travels["des_center"] = travels["des_geo"].apply(lambda geo: geo_to_center_lamb(geo))

    travels["distance_ori"] = [distance(res, ori) for res, ori in zip(travels["res_center"], travels["ori_center"])]
    travels["distance_des"] = [distance(res, des) for res, des in zip(travels["res_center"], travels["des_center"])]

    mask_mobloc = (travels["distance_ori"] < 80 * 1000) & (travels["distance_des"] < 80 * 1000)
    travels.loc[mask_mobloc, "mobloc"] = 1
    travels.loc[~mask_mobloc, "mobloc"] = 0

    travels = travels[["emd_id", "id_trav", "mobloc"]]
    return travels


def load_emd_mobloc(pool, emd_id):
    table_name = "emd_mobloc"
    cols_table = {
        "emd_id": "VARCHAR(50) NOT NULL",
        "id_trav": "VARCHAR(50) NOT NULL",
        "mobloc": "VARCHAR(2) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (emd_id, id_trav) USING BTREE"

    data = compute_mobloc(emd_id)
    load_database(pool, table_name, data, cols_table, keys)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    security = True
    if not security:
        load_emd_mobloc(None, "montpellier")

