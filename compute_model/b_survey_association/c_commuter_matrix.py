import pandas as pd


def get_commuter_matrix(work_flows, work_areas):
    commuter_matrix = pd.merge(work_flows, work_areas[["geo_code", "id", "mass"]],
                               left_on="work_geo_code", right_on="geo_code")\
                        .drop(columns=["geo_code", "distance"])

    # create work_within_commune_attribute
    mask_work_within_commune = commuter_matrix["home_geo_code"] == commuter_matrix["work_geo_code"]
    commuter_matrix.loc[mask_work_within_commune, "work_within_commune"] = 1
    commuter_matrix["work_within_commune"].fillna(0, inplace=True)

    commuter_matrix["mass"] = commuter_matrix.groupby(by=["home_geo_code", "work_geo_code", "mode"])[["mass"]].transform(lambda x: x/x.sum())
    commuter_matrix["flow"] = commuter_matrix["mass"] * commuter_matrix["flow"]
    commuter_matrix.drop(columns=["mass"], inplace=True)

    commuter_matrix.set_index(["home_geo_code", "work_within_commune", "mode"], inplace=True)
    commuter_matrix.sort_index(inplace=True)  # to improve performance

    return commuter_matrix


