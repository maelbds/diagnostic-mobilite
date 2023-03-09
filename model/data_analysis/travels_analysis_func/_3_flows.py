from model.data_analysis.travels_analysis_func.home_work_travels import home_work_travels_flows


def sort_geo_codes(row):
    ori = row["c_geo_code_ori"]
    des = row["c_geo_code_des"]
    if ori < des:
        return [ori, des]
    else:
        return [des, ori]


def compute_flows_by_commune(travels, significance_threshold):
    travels_study = travels[["c_geo_code_ori", "c_geo_code_des", "number", "distance", "ghg_emissions", "id"]].copy()
    travels_study[["number", "distance", "ghg_emissions"]] = travels_study[
        ["number", "distance", "ghg_emissions"]].multiply(travels["w_trav"], axis=0)

    travels_study = travels_study.dropna(subset=["c_geo_code_ori", "c_geo_code_des"])

    # no distinction between A->B & B->A
    travels_study[["c_geo_code_ori", "c_geo_code_des"]] = travels_study[["c_geo_code_ori", "c_geo_code_des"]].apply(
        lambda row: sort_geo_codes(row), axis=1, result_type="expand")

    flows = travels_study.groupby(by=["c_geo_code_ori", "c_geo_code_des"]) \
        .agg({"number": lambda col: col.sum().round(),
              "distance": lambda col: col.sum().round(),
              "ghg_emissions": lambda col: col.sum().round(1),
              "id": lambda col: col.drop_duplicates().count(),
              }).sort_values(by=["distance"], ascending=False)

    mask_significant = flows["id"] > significance_threshold
    flows = flows[mask_significant]
    return flows


def get_flows_commune_all(travels, significance_threshold):
    flows = compute_flows_by_commune(travels, significance_threshold)
    flows = flows.to_dict()
    flows_dict = {c: [list(geocodes) + [value] for geocodes, value in flows[c].items()] for c in flows.keys()}
    return flows_dict


def get_flows_commune_home_work(travels, syn_pop, significance_threshold):
    # To integrate properly
    return home_work_travels_flows(travels, syn_pop, significance_threshold)


def get_flows_commune_all_detailed(travels, significance_threshold):
    travels_study = travels[
        ["c_geo_code_ori", "c_geo_code_des", "number", "distance", "ghg_emissions", "id",
         "reason_ori_name_fr", "reason_des_name_fr", "mode_name_fr"]].copy()
    travels_study[["number", "distance", "ghg_emissions"]] = travels_study[
        ["number", "distance", "ghg_emissions"]].multiply(travels["w_trav"], axis=0)

    travels_study = travels_study.dropna(subset=["c_geo_code_ori", "c_geo_code_des"])
    travels_study[["c_geo_code_ori", "c_geo_code_des"]] = travels_study[
        ["c_geo_code_ori", "c_geo_code_des"]].apply(
        lambda row: sort_geo_codes(row), axis=1, result_type="expand")

    travels_study["reason_work"] = (travels_study["reason_ori_name_fr"] == "travail") | \
                                   (travels_study["reason_des_name_fr"] == "travail")

    main_flows_index = compute_flows_by_commune(travels, significance_threshold).iloc[:20].index
    if len(main_flows_index) == 0:
        return []
    travels_study = travels_study.set_index(keys=["c_geo_code_ori", "c_geo_code_des"])
    main_flows_all = travels_study.loc[main_flows_index]
    main_flows_all.reset_index(inplace=True)

    main_flows_all_total = main_flows_all[
        ["c_geo_code_ori", "c_geo_code_des", "number", "distance", "ghg_emissions", "id"]] \
        .groupby(by=["c_geo_code_ori", "c_geo_code_des"]) \
        .agg({"number": lambda col: col.sum().round(),
              "distance": lambda col: col.sum().round(),
              "ghg_emissions": lambda col: col.sum().round(2),
              "id": lambda col: col.drop_duplicates().count(),
              })

    main_flows_all_total_modes = main_flows_all[
        ["c_geo_code_ori", "c_geo_code_des", "number", "distance", "ghg_emissions", "id", "mode_name_fr"]] \
        .groupby(by=["c_geo_code_ori", "c_geo_code_des", "mode_name_fr"]) \
        .agg({"number": lambda col: col.sum().round(),
              "distance": lambda col: col.sum().round(),
              "ghg_emissions": lambda col: col.sum().round(2),
              "id": lambda col: col.drop_duplicates().count(),
              })
    main_flows_all_total_modes.reset_index(level=["mode_name_fr"], inplace=True)

    main_flows_all_total_reasons_modes = main_flows_all[
        ["c_geo_code_ori", "c_geo_code_des", "number", "distance", "ghg_emissions", "id", "reason_work", "mode_name_fr"]] \
        .groupby(by=["c_geo_code_ori", "c_geo_code_des", "reason_work", "mode_name_fr"]) \
        .agg({"number": lambda col: col.sum().round(),
              "distance": lambda col: col.sum().round(),
              "ghg_emissions": lambda col: col.sum().round(2),
              "id": lambda col: col.drop_duplicates().count().round(),
              })
    main_flows_all_total_reasons_modes.reset_index(level=["reason_work", "mode_name_fr"], inplace=True)

    def combine(od):
        mask_work = main_flows_all_total_reasons_modes["reason_work"]
        main_flows_all_total_modes_reason_work = main_flows_all_total_reasons_modes.where(mask_work).drop(
            columns=["reason_work"])
        main_flows_all_total_modes_reason_other = main_flows_all_total_reasons_modes.where(~mask_work).drop(
            columns=["reason_work"])
        return {
            "geocode1": od[0],
            "geocode2": od[1],
            "total": main_flows_all_total.loc[od].to_dict(),
            "total_modes": main_flows_all_total_modes.loc[od].set_index("mode_name_fr").to_dict(orient="index"),
            "total_modes_reason": {
                "work": main_flows_all_total_modes_reason_work.loc[od].set_index("mode_name_fr").dropna().to_dict(
                    orient="index"),
                "other": main_flows_all_total_modes_reason_other.loc[od].set_index("mode_name_fr").dropna().to_dict(
                    orient="index")}
        }

    od_detailed = [combine(od) for od in main_flows_index]
    return od_detailed


def get_flows_commune_outside(travels, significance_threshold):
    mask_outside = (travels["zone_ori"] == -1) | (travels["zone_des"] == -1)
    travels_outside = travels[mask_outside]

    flows_outside = compute_flows_by_commune(travels_outside, significance_threshold)
    flows_outside_dict = flows_outside.to_dict()
    flows_outside_dict = {c: [list(geocodes) + [value] for geocodes, value in flows_outside_dict[c].items()] for c in
                          flows_outside_dict.keys()}
    return flows_outside_dict


def get_3_flows(travels, syn_pop, territory, significance_threshold):
    return {
        "flows_commune_all": get_flows_commune_all(travels, significance_threshold),
        "flows_commune_home_work": get_flows_commune_home_work(travels, syn_pop, significance_threshold),
        "flows_commune_all_detailed": get_flows_commune_all_detailed(travels, significance_threshold),
        "flows_commune_outside": get_flows_commune_outside(travels, significance_threshold)
    }

