import pandas as pd

from compute_model.database_connection.db_request import db_request
from compute_model.years import COG, year_dossier_complet

# For each attribute used to match the IPU, we have :
# - one function to get the marginal value
# - one function to format the census for IPU (from individuals to households)

year_data = year_dossier_complet


# --- STATUS

def get_marginal_status(geo_code):
    result = db_request(
        """ SELECT retired, employed, unemployed, other, scholars_2_5, 
                   scholars_6_10, scholars_11_14, scholars_15_17, scholars_18
            FROM insee_dossier_complet_status 
            WHERE CODGEO = :geo_code 
            AND year_data = :year_data
            AND year_cog = :year_cog
        """,
        {
            "geo_code": geo_code,
            "year_data": year_data,
            "year_cog": COG
        }
    )
    status = pd.DataFrame(result, columns=["retired", "employed", "unemployed", "other", "scholars_2_5",
                                           "scholars_6_10", "scholars_11_14", "scholars_15_17", "scholars_18"], dtype=int)
    status.rename(columns=lambda name: "status_" + name, inplace=True)
    return status


def format_ipu_status(census):
    cs_ipu = pd.DataFrame()
    cs_ipu["status"] = census["status"]
    cs_ipu_status = pd.get_dummies(cs_ipu['status'], prefix_sep='_', prefix='status', dtype=int)
    cs_ipu = cs_ipu.join(cs_ipu_status)
    cs_ipu = cs_ipu.drop(columns=["status"])

    # to prevent from missing attributes
    status_attributes = [f"status_{l}" for l in ["retired", "employed", "unemployed", "other", "scholars_2_5",
                         "scholars_6_10", "scholars_11_14", "scholars_15_17", "scholars_18"]]
    for col in status_attributes:
        if col not in cs_ipu.columns:
            cs_ipu[col] = 0

    return cs_ipu


# --- WORKERS WITHIN COMMUNE

def get_marginal_workers_within_commune(geo_code):
    result = db_request(
        """ SELECT ACTOCC15P_ILT1
            FROM insee_dossier_complet 
            WHERE CODGEO = :geo_code 
            AND year_data = :year_data
            AND year_cog = :year_cog
        """,
        {
            "geo_code": geo_code,
            "year_data": year_data,
            "year_cog": COG
        }
    )
    work_in_com = pd.DataFrame(result, columns=["workers_within_commune"], dtype=int)
    return work_in_com


def format_ipu_workers_within_commune(census):
    cs_ipu = pd.DataFrame()
    cs_ipu["workers_within_commune"] = census["work_within_commune"]  # already 0 and 1
    return cs_ipu


# --- WORK TRAVEL MODE

def get_marginal_travel_mode(geo_code):
    result = db_request(
        """ SELECT ACTOCC15P_PASTRANS, ACTOCC15P_MARCHE, ACTOCC15P_VELO, 
                   ACTOCC15P_2ROUESMOT, ACTOCC15P_VOITURE,  ACTOCC15P_COMMUN
            FROM insee_dossier_complet 
            WHERE CODGEO = :geo_code 
            AND year_data = :year_data
            AND year_cog = :year_cog
        """,
        {
            "geo_code": geo_code,
            "year_data": year_data,
            "year_cog": COG
        }
    )
    work_mode = pd.DataFrame(result, columns=["1", "2", "3", "4", "5", "6"], dtype=int)
    work_mode.rename(columns=lambda name: "work_travel_mode_" + name, inplace=True)
    return work_mode


def format_ipu_work_travel_mode(census):
    cs_ipu = pd.DataFrame()
    cs_ipu["work_travel_mode"] = census["work_transport"]
    work_travel_mode_ipu = pd.get_dummies(cs_ipu['work_travel_mode'], prefix_sep='_', prefix='work_travel_mode',
                                          dtype=int)
    cs_ipu = cs_ipu.join(work_travel_mode_ipu)
    cs_ipu = cs_ipu.drop(columns=["work_travel_mode", "work_travel_mode_Z"])

    # to prevent from missing attributes
    work_travel_mode_attributes = [f"work_travel_mode_{i}" for i in ["1", "2", "3", "4", "5", "6"]]
    for col in work_travel_mode_attributes:
        if col not in cs_ipu.columns:
            cs_ipu[col] = 0

    return cs_ipu


# --- CSP

def get_marginal_csp(geo_code):
    result = db_request(
        """ SELECT POP15P_CS1, POP15P_CS2, POP15P_CS3, 
                   POP15P_CS4, POP15P_CS5,  POP15P_CS6
            FROM insee_dossier_complet 
            WHERE CODGEO = :geo_code 
            AND year_data = :year_data
            AND year_cog = :year_cog
        """,
        {
            "geo_code": geo_code,
            "year_data": year_data,
            "year_cog": COG
        }
    )
    csp = pd.DataFrame(result, columns=["1", "2", "3", "4", "5", "6"], dtype=int)
    csp.rename(columns=lambda name: "csp_" + name, inplace=True)
    return csp


def format_ipu_csp(census):
    cs_ipu = pd.DataFrame()
    cs_ipu["csp"] = census["csp"]
    cs_ipu_csp = pd.get_dummies(cs_ipu['csp'], prefix_sep='_', prefix='csp', dtype=int)
    cs_ipu = cs_ipu.join(cs_ipu_csp)
    cs_ipu = cs_ipu.drop(columns=["csp", "csp_7", "csp_8"])  # 7 & 8 removed to free liberty degrees (7 already represented with status = retired)

    # to prevent from missing attributes
    csp_attributes = [f"csp_{i}" for i in ["1", "2", "3", "4", "5", "6"]]
    for col in csp_attributes:
        if col not in cs_ipu.columns:
            cs_ipu[col] = 0

    return cs_ipu


# --- CARS NB

def get_marginal_cars_nb(geo_code):
    result = db_request(
        """ SELECT (MEN - RP_VOIT1P), RP_VOIT1, RP_VOIT2P
            FROM insee_dossier_complet 
            WHERE CODGEO = :geo_code 
            AND year_data = :year_data
            AND year_cog = :year_cog
        """,
        {
            "geo_code": geo_code,
            "year_data": year_data,
            "year_cog": COG
        }
    )
    cars_nb = pd.DataFrame(result, columns=["0", "1", "2"], dtype=int).clip(lower=0)
    cars_nb.rename(columns=lambda name: "cars_nb_" + name, inplace=True)
    return cars_nb


def format_ipu_cars_nb(census):
    cs_ipu = pd.DataFrame()
    cs_ipu["cars_nb"] = census["nb_car"]

    cars_nb_ipu = pd.get_dummies(cs_ipu['cars_nb'], prefix_sep='_', prefix='cars_nb', dtype=int)
    cs_ipu = cs_ipu.join(cars_nb_ipu)
    cs_ipu = cs_ipu.drop(columns=["cars_nb"])

    # BE CAREFUL : nb_car attribute is redundant for each person in a household
    # so we have to divide by nb of persons in household
    cs_ipu = cs_ipu.div(census["nb_pers"], axis=0)

    # to prevent from missing attributes
    cars_nb_attributes = [f"cars_nb_{i}" for i in ["0", "1", "2"]]
    for col in cars_nb_attributes:
        if col not in cs_ipu.columns:
            cs_ipu[col] = 0

    return cs_ipu


# --- CHILD NB

def get_marginal_child_nb(geo_code):
    result = db_request(
        """ SELECT NE24F1, NE24F2, NE24F3, NE24F4P
            FROM insee_dossier_complet 
            WHERE CODGEO = :geo_code 
            AND year_data = :year_data
            AND year_cog = :year_cog
        """,
        {
            "geo_code": geo_code,
            "year_data": year_data,
            "year_cog": COG
        }
    )
    child_nb = pd.DataFrame(result, columns=["1", "2", "3", "4"], dtype=int)
    child_nb.rename(columns=lambda name: "child_nb_" + name, inplace=True)
    return child_nb


def format_ipu_child_nb(census):
    cs_ipu = pd.DataFrame()
    cs_ipu["child_nb"] = census["nb_child"]

    child_nb_ipu = pd.get_dummies(cs_ipu['child_nb'], prefix_sep='_', prefix='child_nb', dtype=int)
    cs_ipu = cs_ipu.join(child_nb_ipu)
    cs_ipu = cs_ipu.drop(columns=["child_nb", "child_nb_0"])  # 0 child removed to free liberty degrees : represented with typmr

    # BE CAREFUL : CHILD NB attribute is redundant for each person in a household
    # so we have to divide by nb of persons in household
    cs_ipu = cs_ipu.div(census["nb_pers"], axis=0)

    # to prevent from missing attributes
    child_nb_attributes = [f"child_nb_{i}" for i in ["1", "2", "3", "4"]]
    for col in child_nb_attributes:
        if col not in cs_ipu.columns:
            cs_ipu[col] = 0

    return cs_ipu


# --- TYPMR

def get_marginal_typmr(geo_code):
    result = db_request(
        """ SELECT POP, PMEN, PMEN_MENPSEUL, PMEN_MENSFAM, (PMEN_MENCOUPSENF + PMEN_MENCOUPAENF), PMEN_MENFAMMONO
            FROM insee_dossier_complet 
            WHERE CODGEO = :geo_code 
            AND year_data = :year_data
            AND year_cog = :year_cog
        """,
        {
            "geo_code": geo_code,
            "year_data": year_data,
            "year_cog": COG
        }
    )
    hh_type = pd.DataFrame(result, columns=["tot", "tot_men", "1", "2", "4", "3"], dtype=int)
    if hh_type["tot_men"].min() > 0:
        hh_type = hh_type.mul(hh_type["tot"]/hh_type["tot_men"], axis=0).round()
    hh_type.drop(columns=["tot", "tot_men"], inplace=True)
    hh_type.rename(columns=lambda name: "hh_type_" + name, inplace=True)
    return hh_type


def format_ipu_hh_type(census):
    cs_ipu = pd.DataFrame()
    cs_ipu["hh_type"] = census["hh_type"]

    hh_type_ipu = pd.get_dummies(cs_ipu['hh_type'], prefix_sep='_', prefix='hh_type', dtype=int)
    cs_ipu = cs_ipu.join(hh_type_ipu)
    cs_ipu = cs_ipu.drop(columns=["hh_type"])

    # to prevent from missing attributes
    hh_type_attributes = [f"hh_type_{i}" for i in ["1", "2", "3", "4"]]
    for col in hh_type_attributes:
        if col not in cs_ipu.columns:
            cs_ipu[col] = 0

    return cs_ipu


# ------------------------------------


format_ipu_functions = [
    format_ipu_status,
    format_ipu_workers_within_commune,
    format_ipu_work_travel_mode,
    format_ipu_csp,
    format_ipu_cars_nb,
    format_ipu_child_nb,
    format_ipu_hh_type,
]

marginals_functions = [
    get_marginal_status,
    get_marginal_workers_within_commune,
    get_marginal_travel_mode,
    get_marginal_csp,
    get_marginal_cars_nb,
    get_marginal_child_nb,
    get_marginal_typmr
]


def prepare_census_for_ipu(census):
    return pd.concat([format_func(census) for format_func in format_ipu_functions], axis=1)


def get_marginals(geo_code):
    return pd.concat([marginal_func(geo_code) for marginal_func in marginals_functions], axis=1).iloc[0]


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)
    print(get_marginals("79048"))
