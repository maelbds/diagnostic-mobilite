from model.data_analysis.travels_analysis_func._0_basic_functions import compute_daily_indicator, compute_indicators_by, \
    round_none_case


def get_4_focus(travels, syn_pop, territory, significance_threshold):
    return {
        "work": get_work_travels_output(travels, territory, syn_pop, significance_threshold),
        "home": get_home_travels_output(travels, territory, syn_pop, significance_threshold)
    }


def get_work_travels_output(travels, territory, syn_pop, significance_threshold):
    # work_travels_mask = (travels["reason_des_name"] == "work") | (travels["reason_ori_name"] == "work")
    work_travels_mask = (travels["reason_name_fr"] == "domicile ↔ travail")
    work_travels = travels.loc[work_travels_mask]

    # GENERAL
    pop_employed = syn_pop[syn_pop["status"] == "employed"]

    daily_nb = compute_daily_indicator("number", work_travels, pop_employed, significance_threshold)
    daily_distance = compute_daily_indicator("distance", work_travels, pop_employed, significance_threshold)

    work_travels_by_modes = compute_indicators_by("mode_name_fr", ["number", "distance", "ghg_emissions"],
                                                  work_travels, significance_threshold)

    # new attributes for detailed studies
    work_trvls_study = work_travels[["reason_ori_name", "reason_des_name", "reason_ori_name_fr", "reason_des_name_fr",
                                     "number", "distance", "ghg_emissions", "id"]].copy()

    work_trvls_study["distance_inf7km"] = work_trvls_study["distance"] < 7
    direct_mask = ((work_trvls_study["reason_ori_name"] == "home") & (work_trvls_study["reason_des_name"] == "work")) | \
                  ((work_trvls_study["reason_ori_name"] == "work") & (work_trvls_study["reason_des_name"] == "home"))
    work_trvls_study.loc[direct_mask, "direct"] = "direct"
    work_trvls_study.loc[~direct_mask, "direct"] = "indirect"

    work_trvls_study["indirect_reason_fr"] = work_trvls_study["reason_des_name_fr"]
    mask_work = work_trvls_study["indirect_reason_fr"] == "travail"
    work_trvls_study.loc[mask_work, 'indirect_reason_fr'] = work_trvls_study.loc[mask_work, 'reason_ori_name_fr']

    work_trvls_study = set_distance_class_attr(work_trvls_study)

    work_trvls_study[["number", "distance", "ghg_emissions"]] = work_trvls_study[
        ["number", "distance", "ghg_emissions"]].multiply(work_travels["w_trav"], axis=0)

    # BY DISTANCE CLASS
    work_trvls_by_dist = work_trvls_study[["distance_class", "direct",
                                           "number", "distance", "ghg_emissions", "id"]].groupby(
        by=["distance_class", "direct"], as_index=False).agg({
        "number": lambda col: col.sum().round(),
        "distance": lambda col: col.sum().round(),
        "ghg_emissions": lambda col: col.sum().round(2),
        "id": lambda col: col.drop_duplicates().count(),
    })
    # handling statistical significance
    mask_significance_threshold = work_trvls_by_dist["id"] < significance_threshold
    work_trvls_by_dist.loc[mask_significance_threshold, "distance_class"] = "autre/imprécis"
    work_trvls_by_dist = work_trvls_by_dist.groupby(by=["distance_class", "direct"]).sum()

    work_trvls_by_dist_dict = {c: {l: work_trvls_by_dist.xs(l)[c].to_dict()
                                   for l in work_trvls_by_dist.index.levels[0]}
                               for c in work_trvls_by_dist.columns}

    # BY ASSOCIATED REASON
    work_trvls_by_reason = work_trvls_study[["indirect_reason_fr", "distance_inf7km",
                                             "number", "distance", "ghg_emissions", "id"]].groupby(
        by=["indirect_reason_fr", "distance_inf7km"], as_index=False).agg({
        "number": lambda col: col.sum().round(),
        "distance": lambda col: col.sum().round(),
        "ghg_emissions": lambda col: col.sum().round(2),
        "id": lambda col: col.drop_duplicates().count(),
    })
    # handling statistical significance
    mask_significance_threshold = work_trvls_by_reason["id"] < significance_threshold
    work_trvls_by_reason.loc[mask_significance_threshold, "indirect_reason_fr"] = "autre/imprécis"
    work_trvls_by_reason = work_trvls_by_reason.groupby(by=["indirect_reason_fr", "distance_inf7km"]).sum()

    work_trvls_by_reason_dict = {c: {l: work_trvls_by_reason.xs(l)[c].to_dict()
                                     for l in work_trvls_by_reason.index.levels[0]}
                                 for c in work_trvls_by_reason.columns}

    return {
        "total": {
            "pop": int(pop_employed["w_ind"].sum()),
            "number": round_none_case(daily_nb["total"]),
            "distance": round_none_case(daily_distance["total"]),
            "number_per_mob_pers": round_none_case(daily_nb["per_mobile_person"], 2),
            "distance_per_mob_pers": round_none_case(daily_distance["per_mobile_person"], 1),
        },
        "modes": {
            "number": work_travels_by_modes["number"],
            "distance": work_travels_by_modes["distance"],
        },
        "by_reasons": work_trvls_by_reason_dict,
        "by_distance_class": work_trvls_by_dist_dict
    }


def get_home_travels_output(travels, territory, syn_pop, significance_threshold):
    #home_travels_mask = (travels["reason_des_name"] == "home") | (travels["reason_ori_name"] == "home")
    home_travels_mask = travels["reason_name_fr"].isin(["domicile ↔ études",
                                                        "domicile ↔ achats",
                                                        "domicile ↔ accompagnement",
                                                        "domicile ↔ loisirs",
                                                        "domicile ↔ visites",
                                                        "domicile ↔ affaires personnelles"])
    home_travels = travels[home_travels_mask]

    daily_nb = compute_daily_indicator("number", home_travels, syn_pop, significance_threshold)
    daily_distance = compute_daily_indicator("distance", home_travels, syn_pop, significance_threshold)

    home_travels_by_modes = compute_indicators_by("mode_name_fr", ["number", "distance", "ghg_emissions"],
                                                  home_travels, significance_threshold)

    # new attributes for detailed studies
    home_trvls_study = home_travels[["reason_ori_name", "reason_des_name", "reason_ori_name_fr", "reason_des_name_fr",
                                     "number", "distance", "ghg_emissions", "id"]].copy()

    home_trvls_study["distance_inf7km"] = home_trvls_study["distance"] < 7

    home_trvls_study["indirect_reason_fr"] = home_trvls_study["reason_des_name_fr"]
    mask_home = home_trvls_study["indirect_reason_fr"] == "domicile"
    home_trvls_study.loc[mask_home, 'indirect_reason_fr'] = home_trvls_study.loc[mask_home, 'reason_ori_name_fr']

    home_trvls_study = set_distance_class_attr(home_trvls_study)

    home_trvls_study[["number", "distance", "ghg_emissions"]] = home_trvls_study[
        ["number", "distance", "ghg_emissions"]].multiply(home_travels["w_trav"], axis=0)

    # BY DISTANCE CLASS
    home_trvls_by_dist = home_trvls_study[["distance_class", "number", "distance", "ghg_emissions", "id"]].groupby(
        by=["distance_class"], as_index=False).agg({
        "number": lambda col: col.sum().round(),
        "distance": lambda col: col.sum().round(),
        "ghg_emissions": lambda col: col.sum().round(2),
        "id": lambda col: col.drop_duplicates().count(),
    })
    # handling statistical significance
    mask_significance_threshold = home_trvls_by_dist["id"] < significance_threshold
    home_trvls_by_dist.loc[mask_significance_threshold, "distance_class"] = "autre/imprécis"
    home_trvls_by_dist = home_trvls_by_dist.groupby(by="distance_class").sum()

    home_trvls_by_dist_dict = home_trvls_by_dist.to_dict()

    # BY REASON
    home_trvls_by_reason = home_trvls_study[["indirect_reason_fr", "distance_inf7km",
                                             "number", "distance", "ghg_emissions", "id"]].groupby(
        by=["indirect_reason_fr", "distance_inf7km"], as_index=False).agg({
        "number": lambda col: col.sum().round(),
        "distance": lambda col: col.sum().round(),
        "ghg_emissions": lambda col: col.sum().round(2),
        "id": lambda col: col.drop_duplicates().count(),
    })
    # handling statistical significance
    mask_significance_threshold = home_trvls_by_reason["id"] < significance_threshold
    home_trvls_by_reason.loc[mask_significance_threshold, "indirect_reason_fr"] = "autre/imprécis"
    home_trvls_by_reason = home_trvls_by_reason.groupby(by=["indirect_reason_fr", "distance_inf7km"]).sum()

    home_trvls_by_reason_dict = {c: {l: home_trvls_by_reason.xs(l)[c].to_dict()
                                     for l in home_trvls_by_reason.index.levels[0]}
                                 for c in home_trvls_by_reason.columns}

    return {
        "total": {
            "number": round_none_case(daily_nb["total"]),
            "distance": round_none_case(daily_distance["total"]),
            "number_per_mob_pers": round_none_case(daily_nb["per_mobile_person"], 2),
            "distance_per_mob_pers": round_none_case(daily_distance["per_mobile_person"], 1),
        },
        "modes": {
            "number": home_travels_by_modes["number"],
            "distance": home_travels_by_modes["distance"],
        },
        "by_reasons": home_trvls_by_reason_dict,
        "by_distance_class": home_trvls_by_dist_dict
    }


def set_distance_class_attr(travels):
    travels.loc[travels["distance"] < 1, "distance_class"] = "moins de 1 km"
    travels.loc[(1 <= travels["distance"]) & (travels["distance"] < 5), "distance_class"] = "entre 1 et 5 km"
    travels.loc[(5 <= travels["distance"]) & (travels["distance"] < 7), "distance_class"] = "entre 5 et 7 km"
    travels.loc[(7 <= travels["distance"]) & (travels["distance"] < 10), "distance_class"] = "entre 7 et 10 km"
    travels.loc[(10 <= travels["distance"]) & (travels["distance"] < 20), "distance_class"] = "entre 10 et 20 km"
    travels.loc[travels["distance"] >= 20, "distance_class"] = "plus de 20km"
    return travels
