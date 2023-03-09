from model.data_analysis.travels_analysis_func._0_basic_functions import compute_indicators_by


def get_2_zones(travels, syn_pop, territory, significance_threshold):
    # -------------- modes by zones
    zones = sorted(list(set([c.zone for c in territory.communes] + [-1])))
    zones_modes = {}

    travels_study = travels[["number", "distance", "ghg_emissions", "id"]].copy()
    travels_study[["number", "distance", "ghg_emissions"]] = travels_study[
        ["number", "distance", "ghg_emissions"]].multiply(travels["w_trav"], axis=0)

    for i in zones:
        zones_modes[str(i)] = {}
        for j in zones:
            if j >= i:
                mask_travels_i_j = (travels["zone_ori"] == i) & (travels["zone_des"] == j)
                mask_travels_j_i = (travels["zone_ori"] == j) & (travels["zone_des"] == i)

                travels_zone_i_j = travels.loc[mask_travels_i_j | mask_travels_j_i]
                modes_i_j = compute_indicators_by("mode_name_fr", ["number", "distance", "ghg_emissions"],
                                                  travels_zone_i_j, significance_threshold)
                zones_modes[str(i)][str(j)] = modes_i_j

                travels_study.loc[mask_travels_i_j | mask_travels_j_i, "zones_exchange_type"] = "zones_" + str(
                    i) + "_" + str(j)

    zones_modes_global = travels_study.groupby(by="zones_exchange_type") \
        .agg({"number": lambda col: col.sum().round(),
              "distance": lambda col: col.sum().round(),
              "ghg_emissions": lambda col: col.sum().round(1),
              "id": lambda col: col.drop_duplicates().count(),
              })
    zones_modes_global = zones_modes_global.to_dict()

    mask_missing_zones = travels["zone_ori"].isna() | travels["zone_des"].isna()
    zones_missing = travels_study.loc[mask_missing_zones, ["number", "distance", "ghg_emissions"]].sum().round().to_dict()

    return {"zones_modes": zones_modes,
            "zones_modes_global": zones_modes_global,
            "zones_missing": zones_missing}
