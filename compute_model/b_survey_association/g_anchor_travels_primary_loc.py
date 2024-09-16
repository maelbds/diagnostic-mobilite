import numpy as np
import random
import pandas as pd


def set_residential_location(travels):
    mask_ori_home = travels["reason_ori_name"] == "home"
    travels.loc[mask_ori_home, "id_ori"] = travels.loc[mask_ori_home, "ra_id"]
    mask_des_home = travels["reason_des_name"] == "home"
    travels.loc[mask_des_home, "id_des"] = travels.loc[mask_des_home, "ra_id"]
    return travels


def match_education_location(travels):
    distance_gap = []

    mask_scholars_trav = travels["status"].isin(
        ["scholars_2_5", "scholars_6_10", "scholars_11_14", "scholars_15_17", "scholars_18"])
    scholars = travels.loc[mask_scholars_trav].drop_duplicates(subset="id_ind").sort_values(
        ["main_activity", "main_distance"], ascending=True)

    education_places_distribution = scholars.loc[:, ["ra_id", "education_id", "education_dist"]]
    education_places_distribution = education_places_distribution.groupby(["ra_id", "education_id"]) \
        .agg(distance=("education_dist", "first"),
             count=("education_dist", "count"))

    def find_educ_area(ra_id, main_distance, main_activity):
        if main_activity != "1.4":
            mask_full_ea = education_places_distribution["count"] == 0
            ea = random.choice(education_places_distribution.loc[~mask_full_ea].loc[(ra_id,)].index.values.tolist())
        else:
            if np.isnan(main_distance):
                ea = random.choice(education_places_distribution.loc[(ra_id,)].index.values.tolist())
            else:
                distances = education_places_distribution.loc[(ra_id,), "distance"] - main_distance
                ea = distances.abs().idxmin()

        if not np.isnan(main_distance):
            distance_gap.append(education_places_distribution.loc[(ra_id, ea), "distance"] - main_distance)

        education_places_distribution.loc[(ra_id, ea), "count"] -= 1
        if education_places_distribution.loc[(ra_id, ea), "count"] <= 0:
            education_places_distribution.loc[(ra_id, ea), "distance"] = 1000000
        return ea

    scholars.loc[:, "educ_area_id"] = [find_educ_area(ra_id, main_distance, main_activity)
                                       for ra_id, main_distance, main_activity
                                       in zip(scholars.loc[:, "ra_id"],
                                              scholars.loc[:, "main_distance"],
                                              scholars.loc[:, "main_activity"])]

    travels = pd.merge(travels, scholars.loc[:, ["id_ind", "educ_area_id"]], on="id_ind", how="left")

    mask_ori_educ = travels.loc[:, "reason_ori_name"] == "education"
    travels.loc[mask_ori_educ, "id_ori"] = travels.loc[mask_ori_educ, "educ_area_id"]
    mask_des_educ = travels.loc[:, "reason_des_name"] == "education"
    travels.loc[mask_des_educ, "id_des"] = travels.loc[mask_des_educ, "educ_area_id"]
    travels.drop(columns="educ_area_id", inplace=True)
    return travels


def match_other_location(travels):
    persons = travels.drop_duplicates(subset="id_ind").sort_values(["main_distance"], ascending=True)
    mask_other = ~persons["status"].isin(
        ["employed", "scholars_2_5", "scholars_6_10", "scholars_11_14", "scholars_15_17", "scholars_18"])

    for reason in ["shopping", "services", "leisure"]:
        distance_gap = []
        mask_reason = persons["main_activity_name"] == reason
        other_r = persons.loc[mask_other & mask_reason].copy(deep=False)
        nb_other_r = len(other_r)
        #print(other_r)
        #print(nb_other_r)

        places_distribution = persons.loc[:, ["ra_id", reason + "_id", reason + "_dist"]]
        places_distribution["is_concerned"] = mask_reason
        places_distribution["total_pop"] = 1
        places_distribution = places_distribution.groupby(["ra_id", reason + "_id"]) \
            .agg(distance=(reason + "_dist", "first"),
                 count=(reason + "_dist", "count"),
                 is_concerned=("is_concerned", "sum"),
                 total_pop=("total_pop", "sum"))

        def pond_by_ra_id(places_distribution):
            places_distribution["count"] = places_distribution["count"] * places_distribution["is_concerned"].sum() / places_distribution["total_pop"].sum()
            return places_distribution
        places_distribution = places_distribution.groupby("ra_id").apply(lambda df: pond_by_ra_id(df))

        """print(reason + "_places_distribution")
        print(places_distribution)
        print(places_distribution["count"].sum())
        print((places_distribution["count"]*places_distribution["distance"]).sum()/places_distribution["count"].sum())
        """

        def find_reason_area(ra_id, main_distance):
            if np.isnan(main_distance):
                ra = random.choice(places_distribution.loc[(ra_id,)].index.values.tolist())
            else:
                distances = places_distribution.loc[(ra_id,), "distance"] - main_distance
                ra = distances.abs().idxmin()
            places_distribution.loc[(ra_id, ra), "count"] -= 1

            if not np.isnan(main_distance):
                distance_gap.append(places_distribution.loc[(ra_id, ra), "distance"] - main_distance)

            if places_distribution.loc[(ra_id, ra), "count"] <= 0:
                places_distribution.loc[(ra_id, ra), "distance"] = 1000000
            return ra

        other_r.loc[:, reason + "_area_id"] = [find_reason_area(ra_id, main_distance)
                                               for ra_id, main_distance
                                               in zip(other_r.loc[:, "ra_id"],
                                                      other_r.loc[:, "main_distance"])]

        #print(other_r)
        """print(places_distribution)
        print(places_distribution["count"].sum())"""

        travels = pd.merge(travels, other_r.loc[:, ["id_ind", reason + "_area_id"]], on="id_ind", how="left")
        #print(travels)

        """print(reason + " gap")
        print(np.mean(np.abs(distance_gap)))
        print(np.mean(distance_gap))
        print(np.mean([d for d in distance_gap if d >= 0]))
        print(len([d for d in distance_gap if d >= 0]))
        print(np.mean([d for d in distance_gap if d < 0]))
        print(len([d for d in distance_gap if d < 0]))
        print(np.min(distance_gap))
        print(np.max(distance_gap))"""

        r_trav_ori = travels["reason_ori_name"] == reason
        travels.loc[r_trav_ori, "id_ori"] = travels.loc[r_trav_ori, reason + "_area_id"]
        r_trav_des = travels["reason_des_name"] == reason
        travels.loc[r_trav_des, "id_des"] = travels.loc[r_trav_des, reason + "_area_id"]
        #print(travels)
        travels.drop(columns=reason + "_area_id", inplace=True)
    #print(travels)

    return travels


def match_work_location(travels):
    mask_emp = travels["status"] == "employed"
    people_with_work_trav = travels.loc[mask_emp].drop_duplicates(subset="id_ind")
    people_with_work_trav.loc[:, "work_area_id"] = people_with_work_trav.loc[:, "work_id"]

    travels = pd.merge(travels, people_with_work_trav[["id_ind", "work_area_id"]], on="id_ind", how="left")

    mask_ori_work = travels["reason_ori_name"] == "work"
    travels.loc[mask_ori_work, "id_ori"] = travels.loc[mask_ori_work, "work_area_id"]
    mask_des_work = travels["reason_des_name"] == "work"
    travels.loc[mask_des_work, "id_des"] = travels.loc[mask_des_work, "work_area_id"]
    travels.drop(columns="work_area_id", inplace=True)
    return travels

