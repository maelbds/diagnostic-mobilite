from model.data_analysis.travels_analysis_func._0_basic_functions import compute_daily_indicator, compute_indicators_by, \
    round_none_case


def get_1_key_figures(travels, syn_pop, territory, significance_threshold):
    total_pop = int(syn_pop["w_ind"].sum())
    # to correct with proper w_hh for emd total_hh = int(syn_pop.drop_duplicates(subset=["id_hh"])["w_ind"].sum())

    daily_nb = compute_daily_indicator("number", travels, syn_pop, significance_threshold)
    daily_distance = compute_daily_indicator("distance", travels, syn_pop, significance_threshold)
    daily_duration = compute_daily_indicator("duration", travels, syn_pop, significance_threshold)
    daily_ghg_emissions = compute_daily_indicator("ghg_emissions", travels, syn_pop, significance_threshold)

    week_travels_by_modes = compute_indicators_by("mode_name_fr",
                                                  ["number", "distance", "ghg_emissions"],
                                                  travels, significance_threshold)
    week_travels_by_reasons = compute_indicators_by("reason_name_fr",
                                                    ["number", "distance", "ghg_emissions"],
                                                    travels, significance_threshold)

    return {
        "total": {
            "pop": total_pop,
            #"hh_nb": total_hh,
            "distance": round_none_case(daily_distance["total"]),
            "number": round_none_case(daily_nb["total"]),
            "ghg_emissions": round_none_case(daily_ghg_emissions["total"]),
            "duration": round_none_case(daily_duration["total"]),
            "number_per_mob_pers": round_none_case(daily_nb["per_mobile_person"], 2),
            "distance_per_mob_pers": round_none_case(daily_distance["per_mobile_person"], 1),
            "duration_per_mob_pers": round_none_case(daily_duration["per_mobile_person"]),
        },
        "modes": {
            "number": week_travels_by_modes["number"],
            "distance": week_travels_by_modes["distance"],
            "ghg": week_travels_by_modes["ghg_emissions"],
        },
        "reasons": {
            "number": week_travels_by_reasons["number"],
            "distance": week_travels_by_reasons["distance"],
            "ghg": week_travels_by_reasons["ghg_emissions"],
        }

    }


