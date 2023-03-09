

def compute_daily_indicator(indicator_name, travels, persons, significance_threshold):
    if "immo_lun" in travels.columns:
        total_pop = persons["w_ind"].sum()
        total_pop_immo = (persons["immo_lun"] * persons["w_ind"]).sum() + \
                         (persons["immo_mar"] * persons["w_ind"]).sum() + \
                         (persons["immo_mer"] * persons["w_ind"]).sum() + \
                         (persons["immo_jeu"] * persons["w_ind"]).sum() + \
                         (persons["immo_ven"] * persons["w_ind"]).sum()
        immo_rate = total_pop_immo/total_pop/5
        total_ind_weight = total_pop * (1 - immo_rate)
    else:
        total_ind_weight = travels.drop_duplicates(subset=["id"])["w_ind"].sum()

    #total_hh_weight = travels.drop_duplicates(subset=["id_hh"])["w_ind"].sum()
    total_indicator = (travels["w_trav"] * travels[indicator_name]).sum()

    # handling statistical significance
    nb_enquired = len(travels.drop_duplicates(subset=["id"]))

    if nb_enquired > significance_threshold:
        return {
            "total": total_indicator,
            "per_mobile_person": total_indicator / total_ind_weight,
            #"per_hh": total_indicator / total_hh_weight
        }
    else:
        return {
            "total": None,
            "per_mobile_person": None
        }


def compute_indicators_by(group_by_indicator, indicators, travels, significance_threshold):
    trvls = travels[[group_by_indicator] + indicators + ["id"]].copy()
    trvls[indicators] = trvls[indicators].multiply(travels["w_trav"], axis=0)

    agg_functions = {i: lambda col: col.sum() for i in indicators}
    agg_functions["id"] = lambda col: col.drop_duplicates().count()

    trvls = trvls.groupby(by=group_by_indicator, as_index=False).agg(agg_functions)

    # handling statistical significance
    mask_significance_threshold = trvls["id"] < significance_threshold
    trvls.loc[mask_significance_threshold, group_by_indicator] = "autre/imprécis"

    trvls = trvls[[group_by_indicator] + indicators].groupby(by=group_by_indicator).sum()

    return trvls.to_dict()


def round_none_case(value, ndigits=None):
    return round(value, ndigits) if value is not None else None