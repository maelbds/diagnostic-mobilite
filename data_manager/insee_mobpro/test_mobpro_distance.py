"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import os
import numpy as np
import pandas as pd

from data_manager.db_functions import load_database
from data_manager.insee_general.districts import get_districts
from data_manager.utilities import load_file


def get_flows_from_csv():
    useful_cols = ["LIEU_RESID", "DEP_RESID", "LIEU_TRAV", "IPONDI", "MODTRANS", "TP", "SEXE", "CS1", "EMPL", "TYPMR", "DIST", "DUREE", "DIST_HEBDO", "CHAMP_CO2", "CO2_HEBDO"]
    mobpro = pd.read_csv("data/2019/depl_dom_trav_co2_2019.csv", sep=";", decimal=",", usecols=useful_cols)
    print(mobpro.columns)
    print(mobpro)

    mobpro = mobpro.astype({
        "IPONDI": "float64",
        "LIEU_RESID": "str",
        "DEP_RESID": "str",
        "LIEU_TRAV": "str",
    })

    mobpro["LIEU_RESID"] = mobpro["LIEU_RESID"].apply(lambda x: "0" + x if len(x) == 4 else x)
    mobpro["LIEU_TRAV"] = mobpro["LIEU_TRAV"].apply(lambda x: "0" + x if len(x) == 4 else x)

    print(f"Dist moyenne DT {(mobpro['DIST'] * mobpro['IPONDI']).sum() / mobpro['IPONDI'].sum()}")

    mask_commune = mobpro["LIEU_RESID"] == "59350"
    mask_trans1 = mobpro["MODTRANS"] == 1
    mask_co2 = mobpro["CHAMP_CO2"]
    mask_dist = ((mobpro["MODTRANS"]) == 2 & (mobpro["DIST"] <= 10)) | \
                ((mobpro["MODTRANS"]) == 3 & (mobpro["DIST"] <= 30)) | \
                ((mobpro["MODTRANS"]).isin([4, 5, 6]) & (mobpro["DIST"] <= 100))


    mobpro_a = mobpro.loc[mask_commune & mask_co2]

    nb_actifs = mobpro_a["IPONDI"].sum()
    total_CO2 = (mobpro_a["IPONDI"] * mobpro_a["CO2_HEBDO"]).sum() * 365/7 / 1000

    print(f"actifs : {nb_actifs}")
    print(f"total CO2 : {total_CO2}")
    print(f"CO2e annuelles par pers : {round(total_CO2/nb_actifs)}")

    mobpro_a = mobpro.loc[mask_commune & mask_co2 & mask_dist]

    nb_actifs = mobpro_a["IPONDI"].sum()
    total_CO2 = (mobpro_a["IPONDI"] * mobpro_a["CO2_HEBDO"]).sum() * 365/7 / 1000

    print(f"actifs : {nb_actifs}")
    print(f"total CO2 : {total_CO2}")
    print(f"CO2e annuelles par pers : {round(total_CO2/nb_actifs)}")

    return mobpro


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    get_flows_from_csv()