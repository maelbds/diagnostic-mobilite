import pandas as pd
import numpy as np
import random
import time


# -------------- PRIMARY LOC ASSIGNMENT ----------------------


def set_residential_location(travels):
    res_trav_ori = travels["reason_ori_name"] == "home"
    travels.loc[res_trav_ori, "id_ori"] = travels.loc[res_trav_ori, "ra_id"]
    res_trav_des = travels["reason_des_name"] == "home"
    travels.loc[res_trav_des, "id_des"] = travels.loc[res_trav_des, "ra_id"]
    return travels


def match_work_location(travels):
    mask_emp = travels["status"] == "employed"
    people_with_work_trav = travels.loc[mask_emp].drop_duplicates(subset="id")
    people_with_work_trav.loc[:, "work_area_id"] = people_with_work_trav.loc[:, "work_id"]
    travels = pd.merge(travels, people_with_work_trav[["id", "work_area_id"]], on="id", how="left")

    work_trav_ori = travels["reason_ori_name"] == "work"
    travels.loc[work_trav_ori, "id_ori"] = travels.loc[work_trav_ori, "work_area_id"]
    work_trav_des = travels["reason_des_name"] == "work"
    travels.loc[work_trav_des, "id_des"] = travels.loc[work_trav_des, "work_area_id"]
    travels.drop(columns="work_area_id", inplace=True)
    return travels


def match_education_location(travels, areas, distances_matrix):
    distance_gap = []

    mask_scholars_trav = travels["status"].isin(
        ["scholars_2_5", "scholars_6_10", "scholars_11_14", "scholars_15_17", "scholars_18"])
    scholars = travels.loc[mask_scholars_trav].drop_duplicates(subset="id").sort_values(
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
    travels = pd.merge(travels, scholars.loc[:, ["id", "educ_area_id"]], on="id", how="left")

    educ_trav_ori = travels.loc[:, "reason_ori_name"] == "education"
    travels.loc[educ_trav_ori, "id_ori"] = travels.loc[educ_trav_ori, "educ_area_id"]
    educ_trav_des = travels.loc[:, "reason_des_name"] == "education"
    travels.loc[educ_trav_des, "id_des"] = travels.loc[educ_trav_des, "educ_area_id"]
    travels.drop(columns="educ_area_id", inplace=True)
    return travels


def match_other_location(travels, areas, distances_matrix):
    persons = travels.drop_duplicates(subset="id").sort_values(["main_distance"], ascending=True)
    mask_other = ~persons["status"].isin(
        ["employed", "scholars_2_5", "scholars_6_10", "scholars_11_14", "scholars_15_17", "scholars_18"])

    for reason in ["shopping", "services", "leisure"]:
        distance_gap = []
        mask_reason = persons["main_activity_name"] == reason
        other_r = persons.loc[mask_other & mask_reason]
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

        travels = pd.merge(travels, other_r.loc[:, ["id", reason + "_area_id"]], on="id", how="left")

        r_trav_ori = travels["reason_ori_name"] == reason
        travels.loc[r_trav_ori, "id_ori"] = travels.loc[r_trav_ori, reason + "_area_id"]
        r_trav_des = travels["reason_des_name"] == reason
        travels.loc[r_trav_des, "id_des"] = travels.loc[r_trav_des, reason + "_area_id"]
        travels.drop(columns=reason + "_area_id", inplace=True)
    return travels


# -------------- SECONDARY LOC ASSIGNMENT ----------------------


def complete_activity_chain_1(chain, distances_matrix):
    if chain.iloc[0]["is_id_ori"]:
        id_ori = chain.iloc[0]["id_ori"]
        dist = chain.iloc[0]["distance"]
        reason = chain.iloc[0]["reason_des_name"]
        if reason == "accompany":
            reason = ["education", "leisure", "services", "visits"]
        if reason == "other":
            return chain
        distances = (distances_matrix.loc[(reason,), id_ori] - dist).abs()
        id_des = distances[distances == distances.min()].index[0]
        if type(id_des) != np.int64:
            id_des = id_des[1]
        chain["id_des"] = id_des
        return chain

    elif chain.iloc[0]["is_id_des"]:
        id_des = chain.iloc[0]["id_des"]
        dist = chain.iloc[0]["distance"]
        reason = chain.iloc[0]["reason_ori_name"]
        if reason == "accompany":
            reason = ["education", "leisure", "services", "visits"]
        if reason == "other":
            return chain
        distances = (distances_matrix.loc[(reason,), id_des] - dist).abs()
        id_ori = distances[distances == distances.min()].index[0]
        if type(id_ori) != np.int64:
            id_ori = id_ori[1]
        chain["id_ori"] = id_ori
        return chain
    return


def complete_activity_chain_2(chain, distances_matrix):
    if chain.iloc[0].loc["is_id_ori"] and chain.iloc[-1].loc["is_id_des"]:
        reason = chain.iloc[0].loc["reason_des_name"]
        id1 = chain.iloc[0].loc["id_ori"]
        dist1 = chain.iloc[0].loc["distance"]
        id2 = chain.iloc[-1].loc["id_des"]
        dist2 = chain.iloc[-1].loc["distance"]
        if reason == "accompany":
            reason = ["education", "leisure", "services", "visits"]
        if reason == "other":
            return chain
        distances1 = (distances_matrix.loc[(reason,), id1] - dist1).abs()
        distances2 = (distances_matrix.loc[(reason,), id2] - dist2).abs()
        distances = distances1 + distances2
        id = distances[distances == distances.min()].index[0]
        if type(id) != np.int64:
            id = id[1]
        chain.iloc[0, chain.columns.get_loc('id_des')] = id
        chain.iloc[-1, chain.columns.get_loc('id_ori')] = id
        return chain
    return chain


def complete_activity_chain_3(chain, distances_matrix):
    if chain.iloc[0].loc["is_id_ori"] and chain.notna().iloc[-1].loc["is_id_des"]:
        reason = chain.iloc[0].loc["reason_des_name"]
        id_f = chain.iloc[0].loc["id_ori"]
        id_l = chain.iloc[-1].loc["id_des"]
        dist1 = chain.iloc[0].loc["distance"]
        dist2 = chain.iloc[1].loc["distance"]
        dist3 = chain.iloc[2].loc["distance"]
        if reason in ["other", "accompany"]:
            return chain
        distances1 = (distances_matrix.loc[(reason,), id_f] - dist1).abs()
        distances3 = (distances_matrix.loc[(reason,), id_l] - dist3).abs()

        distances13 = pd.DataFrame({id_3: distances1 + distances3.loc[id_3] for id_3 in distances3.index})
        distances2 = pd.DataFrame({id_3: [abs(distances_matrix[id_3].xs(id_1, level="id").iloc[0] - dist2)
                                          for id_1 in distances1.index]
                                   for id_3 in distances3.index})
        distances2 = distances2 + distances13

        min_dist = distances2[distances2 == distances2.min().min()].dropna(axis=0, how="all").dropna(axis=1, how="all")
        id_1 = min_dist.index[0]
        id_3 = min_dist.columns[0]

        chain.iloc[0, chain.columns.get_loc('id_des')] = id_1
        chain.iloc[1, chain.columns.get_loc('id_ori')] = id_1
        chain.iloc[1, chain.columns.get_loc('id_des')] = id_3
        chain.iloc[2, chain.columns.get_loc('id_ori')] = id_3
        return chain
    return chain


def match_secondary_location(travels, areas, distances_matrix):
    # Create distance matrix by category
    category_distance_matrix = distances_matrix.copy()
    areas_id_reason = pd.DataFrame({"id": [a.id for a in areas],
                                    "reason": [a.reason if a.reason != "residential" else "visits" for a in areas]}
                                   ).set_index("id")
    categories_ids = [[areas_id_reason.loc[a_id, "reason"] for a_id in distances_matrix.index.values],
                      distances_matrix.index.values]
    index_with_categories = pd.MultiIndex.from_arrays(categories_ids, names=("reason", "id"))
    category_distance_matrix = category_distance_matrix.set_index(index_with_categories).sort_index()

    chain_length = [0] * 20

    # Identifying activity chains for each person
    travels = travels.sort_values(["id", "trav_nb"])
    travels["is_id_ori"] = travels["id_ori"].notna()
    travels["is_id_des"] = travels["id_des"].notna()
    travels["chain_id"] = travels["is_id_ori"].groupby(travels["id"]).transform(lambda x: x.cumsum())

    # Matching each activity chain
    def match_by_activity_chain(activity_chain):
        len_chain = len(activity_chain.index)
        if (~activity_chain[["is_id_ori", "is_id_des"]]).sum().sum() > 0:
            chain_length[len_chain] += 1
            if len_chain == 1:
                return complete_activity_chain_1(activity_chain, category_distance_matrix)
            elif len_chain == 2:
                return complete_activity_chain_2(activity_chain, category_distance_matrix)
            elif len_chain == 3:
                return  # complete_activity_chain_3(activity_chain, category_distance_matrix)
            else:
                return
        else:
            return

    travels_matched = travels.groupby(["id", "chain_id"], as_index=False, group_keys=False).apply(
        match_by_activity_chain)
    travels.loc[travels_matched.index] = travels_matched
    #print(chain_length)
    return travels
