import pandas as pd


def complete_activity_chain_1(chain, distances_matrix):
    if chain.iloc[0]["is_id_ori"]:
        id_ori = chain.iloc[0]["id_ori"]
        dist = chain.iloc[0]["distance"]
        reason = chain.iloc[0]["reason_des_name"]
        if reason == "accompany":
            reason = ["education", "leisure", "services", "visits"]
        elif reason == "other":
            return chain
        else:
            reason = [reason]

        distances = (distances_matrix.loc[(reason,), id_ori] - dist).abs()

        id_des = distances.idxmin()[1]
        chain["id_des"] = id_des
        return chain

    elif chain.iloc[0]["is_id_des"]:
        id_des = chain.iloc[0]["id_des"]
        dist = chain.iloc[0]["distance"]
        reason = chain.iloc[0]["reason_ori_name"]
        if reason == "accompany":
            reason = ["education", "leisure", "services", "visits"]
        elif reason == "other":
            return chain
        else:
            reason = [reason]

        distances = (distances_matrix.loc[(reason,), id_des] - dist).abs()

        id_ori = distances.idxmin()[1]
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
        elif reason == "other":
            return chain
        else:
            reason = [reason]

        distances1 = (distances_matrix.loc[(reason,), id1] - dist1).abs()
        distances2 = (distances_matrix.loc[(reason,), id2] - dist2).abs()
        distances = distances1 + distances2

        id = distances.idxmin()[1]
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
    print("category_distance_matrix_copied")
    areas_id_reason = pd.DataFrame({"id": [a_id for a_id in areas["id"]],
                                    "reason": [a_reason if a_reason != "residential" else "visits" for a_reason in areas["reason"]]}
                                   ).set_index("id")
    categories_ids = [[areas_id_reason.loc[a_id, "reason"] for a_id in distances_matrix.index.values],
                      distances_matrix.index.values]
    index_with_categories = pd.MultiIndex.from_arrays(categories_ids, names=("reason", "id"))
    category_distance_matrix = category_distance_matrix.set_index(index_with_categories).sort_index()
    print("category_distance_matrix indexed")

    # Identifying activity chains for each person
    travels = travels.sort_values(["id_ind", "trav_nb"])
    travels["is_id_ori"] = travels["id_ori"].notna()
    travels["is_id_des"] = travels["id_des"].notna()
    travels["chain_id"] = travels["is_id_ori"].groupby(travels["id_ind"]).transform(lambda x: x.cumsum())

    # set chain length
    len_chain = travels.groupby(["id_ind", "chain_id"]).size().rename("chain_len")
    travels = pd.merge(travels, len_chain, left_on=["id_ind", "chain_id"], right_index=True)

    # is chain ori & des known ?
    ori_des_chain = travels.groupby(["id_ind", "chain_id"]).agg(**{
        "is_id_ori_chain": pd.NamedAgg(column="is_id_ori", aggfunc="first"),
        "is_id_des_chain": pd.NamedAgg(column="is_id_des", aggfunc="last"),
    })
    travels = pd.merge(travels, ori_des_chain, left_on=["id_ind", "chain_id"], right_index=True)

    # masks of chain to complete
    mask_chain_length_1_find_ori = (travels["chain_len"] == 1) & ~travels["is_id_ori"] & travels["is_id_des"]
    mask_chain_length_1_find_des = (travels["chain_len"] == 1) & travels["is_id_ori"] & ~travels["is_id_des"]
    mask_chain_length_2 = (travels["chain_len"] == 2) & travels["is_id_ori_chain"] & travels["is_id_des_chain"]

    def find_ch1(id_des, dist, reason):
        if reason == "accompany":
            reason = ["education", "leisure", "services", "visits"]
        elif reason == "other":
            return None
        else:
            reason = [reason]

        distances = (category_distance_matrix.loc[(reason,), id_des] - dist).abs()
        id_ori = distances.idxmin()[1]
        return id_ori

    def find_ch2(id1, id2, dist1, dist2, reason):
        if reason == "accompany":
            reason = ["education", "leisure", "services", "visits"]
        elif reason == "other":
            return None
        else:
            reason = [reason]

        distances1 = (category_distance_matrix.loc[(reason,), id1] - dist1).abs()
        distances2 = (category_distance_matrix.loc[(reason,), id2] - dist2).abs()
        distances = distances1 + distances2

        id = distances.idxmin()[1]
        return id

    # complete chain of length 1
    travels.loc[mask_chain_length_1_find_ori, "id_ori"] = [find_ch1(id_des, dist, reason) for id_des, dist, reason
                                                           in zip(travels.loc[mask_chain_length_1_find_ori, "id_des"],
                                                                  travels.loc[mask_chain_length_1_find_ori, "distance"],
                                                                  travels.loc[mask_chain_length_1_find_ori, "reason_ori_name"])]

    print("ch1 id_ori")
    travels.loc[mask_chain_length_1_find_des, "id_des"] = [find_ch1(id_ori, dist, reason) for id_ori, dist, reason
                                                           in zip(travels.loc[mask_chain_length_1_find_des, "id_ori"],
                                                                  travels.loc[mask_chain_length_1_find_des, "distance"],
                                                                  travels.loc[mask_chain_length_1_find_des, "reason_des_name"])]

    print("ch1_id_des")

    # compute attributes to allocate chain 2
    attr_chain_2 = travels.loc[mask_chain_length_2].groupby(["id_ind", "chain_id"]).agg(**{
        "ch2_id_ori": pd.NamedAgg(column="id_ori", aggfunc="first"),
        "ch2_id_des": pd.NamedAgg(column="id_des", aggfunc="last"),
        "ch2_dist_1": pd.NamedAgg(column="distance", aggfunc="first"),
        "ch2_dist_2": pd.NamedAgg(column="distance", aggfunc="last"),
        "ch2_reason": pd.NamedAgg(column="reason_des_name", aggfunc="first"),
    })
    attr_chain_2["ch2_order"] = 1
    travels = pd.merge(travels, attr_chain_2, left_on=["id_ind", "chain_id"], right_index=True, how="left")
    travels.loc[mask_chain_length_2, "ch2_order"] = travels.loc[mask_chain_length_2].\
        groupby(by=["id_ind", "chain_id"])["ch2_order"].transform(lambda x: x.cumsum())

    mask_travels_ch2_first = travels["ch2_order"] == 1
    mask_travels_ch2_second = travels["ch2_order"] == 2

    # complete chain of length 2
    travels.loc[mask_travels_ch2_first, "id_ch2"] = [find_ch2(id_ori, id_des, dist1, dist2, reason)
                                                     for id_ori, id_des, dist1, dist2, reason
                                                     in zip(travels.loc[mask_travels_ch2_first, "ch2_id_ori"],
                                                            travels.loc[mask_travels_ch2_first, "ch2_id_des"],
                                                            travels.loc[mask_travels_ch2_first, "ch2_dist_1"],
                                                            travels.loc[mask_travels_ch2_first, "ch2_dist_2"],
                                                            travels.loc[mask_travels_ch2_first, "ch2_reason"])]
    travels.loc[mask_travels_ch2_first, "id_des"] = travels.loc[mask_travels_ch2_first, "id_ch2"]
    travels.loc[mask_travels_ch2_second, "id_ori"] = travels.loc[mask_travels_ch2_first, "id_ch2"].to_list()

    print("ch2")

    """ 
    ---- old method
    
    def find_ch2(chain):
        reason = chain.iloc[0].loc["reason_des_name"]
        id1 = chain.iloc[0].loc["id_ori"]
        dist1 = chain.iloc[0].loc["distance"]
        id2 = chain.iloc[-1].loc["id_des"]
        dist2 = chain.iloc[-1].loc["distance"]
        if reason == "accompany":
            reason = ["education", "leisure", "services", "visits"]
        elif reason == "other":
            return chain
        else:
            reason = [reason]

        distances1 = (category_distance_matrix.loc[(reason,), id1] - dist1).abs()
        distances2 = (category_distance_matrix.loc[(reason,), id2] - dist2).abs()
        distances = distances1 + distances2

        id = distances.idxmin()[1]
        chain.iloc[0, chain.columns.get_loc('id_des')] = id
        chain.iloc[-1, chain.columns.get_loc('id_ori')] = id
        return chain[["id_ori", "id_des"]]

    for index, chain in travels.loc[mask_chain_length_2].groupby(["id_ind", "chain_id"]):
        travels.loc[chain.index, ["id_ori", "id_des"]] = find_ch2(chain)
    
    ----  old old method
    travels_matched = travels.loc[mask_chain_length_2].\
        groupby(["id_ind", "chain_id"], as_index=False, group_keys=False).\
        apply(find_ch2)
    travels_matched.dropna(subset=["id_ind"], inplace=True)
    travels.loc[travels_matched.index] = travels_matched
    """

    travels.drop(columns=["is_id_ori", "is_id_des", "chain_id", "chain_len", "is_id_ori_chain", "is_id_des_chain",
                          "id_ch2", "ch2_order", "ch2_dist_1", "ch2_dist_2", "ch2_id_ori", "ch2_id_des", "ch2_reason"],
                 inplace=True)

    return travels

