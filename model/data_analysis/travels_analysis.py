import pandas as pd
import numpy as np
import pprint

from model.data_analysis.travels_analysis_func._1_key_figures import get_1_key_figures
from model.data_analysis.travels_analysis_func._2_zones import get_2_zones
from model.data_analysis.travels_analysis_func._3_flows import get_3_flows
from model.data_analysis.travels_analysis_func._4_focus import get_4_focus


significance_threshold = 30


def get_travels_analysis(travels, syn_pop, territory):
    mask_week = travels["day_type"] == 1
    week_travels = travels.loc[mask_week]

    return {
        "1_key_figures": get_1_key_figures(week_travels, syn_pop, territory, significance_threshold),
        "2_zones": get_2_zones(week_travels, syn_pop, territory, significance_threshold),
        "3_flows": get_3_flows(week_travels, syn_pop, territory, significance_threshold),
        "4_focus": get_4_focus(week_travels, syn_pop, territory, significance_threshold)
    }

