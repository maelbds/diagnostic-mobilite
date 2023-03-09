import pandas as pd


def home_work_travels_flows(travels, persons, significance_threshold):
    travels = travels.copy()
    if "geo_code" not in travels.columns:
        travels = pd.merge(travels, persons[["id_ind", "geo_code"]], on="id_ind")

    travels = travels.sort_values(by=["id", "trav_nb"])

    mask_home_ori = travels["reason_ori_name"] == "home"
    travels.loc[mask_home_ori, "home_marker_ori"] = 1
    travels.loc[~mask_home_ori, "home_marker_ori"] = 0
    mask_home_des = travels["reason_des_name"] == "home"
    travels.loc[mask_home_des, "home_marker_des"] = 1
    travels.loc[~mask_home_des, "home_marker_des"] = 0

    mask_work_ori = travels["reason_ori_name"] == "work"
    travels.loc[mask_work_ori, "work_marker_ori"] = 1
    travels.loc[~mask_work_ori, "work_marker_ori"] = 0
    mask_work_des = travels["reason_des_name"] == "work"
    travels.loc[mask_work_des, "work_marker_des"] = 1
    travels.loc[~mask_work_des, "work_marker_des"] = 0

    travels["count"] = 1
    #print(travels)

    travels["marker_ori"] = travels["home_marker_ori"] + travels["work_marker_ori"]
    travels["home_work_part"] = travels[["id", "marker_ori"]].groupby("id", as_index=False).cumsum()
    #print(travels)

    travels_part = travels[["id", "home_work_part",
                            "home_marker_ori", "work_marker_des",
                            "w_trav",
                            "c_geo_code_ori", "c_geo_code_des", "geo_code",
                            "distance", "ghg_emissions", "count"]]\
        .groupby(by=["id", "home_work_part"], as_index=False)\
        .agg(
        **{
            "home_marker_ori": pd.NamedAgg(column="home_marker_ori", aggfunc="sum"),
            "work_marker_des": pd.NamedAgg(column="work_marker_des", aggfunc="sum"),
            "w_trav": pd.NamedAgg(column="w_trav", aggfunc="first"),
            "geo_code": pd.NamedAgg(column="geo_code", aggfunc="first"),
            "c_geo_code_ori": pd.NamedAgg(column="c_geo_code_ori", aggfunc="first"),
            "c_geo_code_des": pd.NamedAgg(column="c_geo_code_des", aggfunc="last"),
            "distance": pd.NamedAgg(column="distance", aggfunc="sum"),
            "ghg_emissions": pd.NamedAgg(column="ghg_emissions", aggfunc="sum"),
            "count": pd.NamedAgg(column="count", aggfunc="sum"),
        })
    #print(travels_part)

    travels_part["marker_home_work"] = travels_part["home_marker_ori"] + travels_part["work_marker_des"]
    travels_part_home_work = travels_part[travels_part["marker_home_work"] == 2]
    travels_part_home_work["number"] = 1
    #print(travels_part_home_work)

    travels_part_home_work = travels_part_home_work.drop_duplicates(subset="id")
    #print("drop_duplicates")
    #print(travels_part_home_work)

    # -------------- origin/destination flows

    week_travels_od = travels_part_home_work[
        ["c_geo_code_ori", "c_geo_code_des", "geo_code", "number", "distance", "ghg_emissions", "id"]].copy()
    week_travels_od[["number", "distance", "ghg_emissions"]] = week_travels_od[
        ["number", "distance", "ghg_emissions"]].multiply(travels_part_home_work["w_trav"], axis=0)
    week_travels_od = week_travels_od.dropna(subset=["c_geo_code_ori", "c_geo_code_des"])
    week_travels_od["count"] = 1

    def sort_geo_codes(row):
        ori = row["c_geo_code_ori"]
        des = row["c_geo_code_des"]
        home = row["geo_code"]
        if ori == home:
            return [ori, des]
        elif des == home:
            return [des, ori]
        if ori < des:
            return [ori, des]
        else:
            return [des, ori]

    week_travels_od[["c_geo_code_ori", "c_geo_code_des"]] = week_travels_od[["c_geo_code_ori", "c_geo_code_des", "geo_code"]].apply(
        lambda row: sort_geo_codes(row), axis=1, result_type="expand")

    #print(week_travels_od["number"].sum())

    od = week_travels_od[["c_geo_code_ori", "c_geo_code_des", "number", "distance", "ghg_emissions", "count", "id"]] \
        .groupby(by=["c_geo_code_ori", "c_geo_code_des"]) \
        .agg({"number": lambda col: col.sum().round(),
              "distance": lambda col: col.sum().round(),
              "ghg_emissions": lambda col: col.sum().round(),
              "count": lambda col: col.sum(),
              "id": lambda col: col.drop_duplicates().count(),
              }) \
        .sort_values(by=["distance"], ascending=False)
    #print(od)
    mask_low_count = od["id"] > significance_threshold
    od = od[mask_low_count]

    #print(od.apply(lambda col: round(col / col.sum() * 100, 1) if col.sum() != 0 else col))
    od_dict = od.to_dict()
    #print(od_dict)
    od_dict = {c: [list(geocodes) + [value] for geocodes, value in od_dict[c].items()] for c in od_dict.keys()}
    #print(od_dict)
    #travels_output["flows_od"] = od_dict
    return od_dict