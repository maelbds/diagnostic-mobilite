import pandas as pd
import numpy as np


def compute_ori_des_geocode(travels, areas):
    areas_ori = areas[["id", "geo_code"]].rename(columns={"id": "id_ori", "geo_code": "geo_code_ori"})
    areas_des = areas[["id", "geo_code"]].rename(columns={"id": "id_des", "geo_code": "geo_code_des"})

    travels = pd.merge(travels, areas_ori, on="id_ori", how="left")
    travels = pd.merge(travels, areas_des, on="id_des", how="left")

    return travels


def compute_distance(travels, distance_matrix):
    travels["distance_adjusted"] = travels[["id_ori", "id_des"]].apply(
        lambda row: distance_matrix.loc[row["id_ori"], row["id_des"]] if row.notna().all() else None, axis=1)

    # keep EMP distance for unknown computed distance
    mask_dist_none = travels["distance_adjusted"].isna()
    travels.loc[mask_dist_none, "distance_adjusted"] = travels.loc[mask_dist_none, "distance"]

    travels = travels.rename(columns={"distance": "distance_emp", "distance_adjusted": "distance"})
    return travels


def format_travels(travels):
    travels["id_trav_emp"] = travels["id_trav"]
    travels["id_trav"] = travels["geo_code"] + "_" + travels.index.astype(str)
    travels["distance"] = travels["distance"].round(1)
    travels["distance_emp"] = travels["distance_emp"].round(1)

    travels = travels[["id_ind", "id_trav", "w_trav",
                       "geo_code",
                       "distance",
                       "geo_code_ori", "geo_code_des",
                       "id_trav_emp"]]

    return travels

