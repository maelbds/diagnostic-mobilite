import pandas as pd
import os
import numpy as np

from data_manager.db_functions import load_database
from data_manager.emp.prepare_emp import prepare_persons_with_hh, create_status, \
    create_csp, create_dist_pt, prepare_travels, create_day_type, create_immo_days
from data_manager.emp.enrich_emp import get_main_activity_and_dist, get_work_transport_dist, \
    get_chained_work_dist
from data_manager.utilities import load_file


def download_files():
    # reference : "https://www.statistiques.developpement-durable.gouv.fr/resultats-detailles-de-lenquete-mobilite-des-personnes-de-2019?rubrique=60&dossier=1345"

    files = [{
        "name": "Enquête Mobilité des Personnes (EMP) 2018",
        "url": "https://www.statistiques.developpement-durable.gouv.fr/sites/default/files/2023-10/emp_2019_donnees_individuelles_anonymisees.zip",
        "dir": "data/2018",
        "zip_name": "emp2018.zip",
        "file_name": "tcm_ind_public_V3.csv",
    }]

    [load_file(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def read_csv(file_name, variables_name, sep=","):
    variables = pd.read_csv(
        "data/2018/variables.csv",
        sep=";", dtype=str)
    cols = variables[variables_name].dropna().apply(lambda x: x.upper()).tolist()
    data = pd.read_csv(file_name, sep=sep, dtype=str, #encoding_errors="replace",
                       usecols=lambda x: x.upper() in cols)
    return data


def get_emp():
    # HOUSEHOLDS
    tcm_menage = read_csv(
        "data/2018/tcm_men_public_V3.csv",
        "TCM_MEN", ","
    )
    q_menage = read_csv(
        "data/2018/q_menage_public_V3.csv",
        "Q_MENAGE", ";"
    )
    households = pd.merge(tcm_menage, q_menage, left_on="ident_men", right_on="IDENT_MEN").drop(columns=["IDENT_MEN"])

    # PEOPLE
    tcm_ind_kish = read_csv(
        "data/2018/tcm_ind_kish_public_V3.csv",
        "TCM_IND_KISH_public", ";"
    )
    k_individu = read_csv(
        "data/2018/k_individu_public_V3.csv",
        "K_INDIVIDU", ";"
    )
    persons = pd.merge(tcm_ind_kish, k_individu, left_on="ident_ind", right_on="IDENT_IND").drop(columns=["IDENT_IND"])

    # COMBINED
    persons_with_hh = pd.merge(persons, households, left_on="ident_men", right_on="ident_men")

    # CLEANING DATA
    persons_with_hh = prepare_persons_with_hh(persons_with_hh)

    # COMPUTE VARIABLES
    persons_with_hh = create_csp(persons_with_hh)
    persons_with_hh = create_day_type(persons_with_hh)
    persons_with_hh = create_status(persons_with_hh)
    persons_with_hh = create_dist_pt(persons_with_hh)
    persons_with_hh = create_immo_days(persons_with_hh)

    # TRAVELS
    travels = read_csv(
        "data/2018/k_deploc_public_V3.csv",
        "K_DEPLOC", ","
    )

    # CLEANING DATA
    travels = prepare_travels(travels)

    # CREATE MAIN ACTIVITY AND DIST
    persons_with_hh_and_activities = get_main_activity_and_dist(persons_with_hh, travels)

    # COMPUTE CHAINED WORK DIST FOR EMPLOYED PEOPLE
    persons_with_hh_and_activities = get_chained_work_dist(persons_with_hh_and_activities, travels)

    # CREATE WORK_TRANSPORT & WORK_DIST
    persons_with_hh_and_activities = get_work_transport_dist(persons_with_hh_and_activities, travels)

    persons_with_hh_and_activities = persons_with_hh_and_activities.replace({np.nan: None})
    travels = travels.replace({np.nan: None})

    print(travels)
    print(persons_with_hh_and_activities)

    return persons_with_hh_and_activities, travels


def load_emp_persons(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    persons, travels = get_emp()

    cols_table = {
        "ident_ind": "VARCHAR(50) NOT NULL",
        "ident_men": "VARCHAR(50) NOT NULL",
        "pond_indC": "VARCHAR(50) NOT NULL",
        "MDATE_jour": "VARCHAR(50) NULL DEFAULT NULL",
        "TYPEJOUR": "INT(2) NULL DEFAULT NULL",
        "SEXE": "INT(2) NULL DEFAULT NULL",
        "AGE": "INT(3) NULL DEFAULT NULL",
        "DEP_RES": "VARCHAR(4) NULL DEFAULT NULL",
        "CS24": "INT(5) NULL DEFAULT NULL",
        "SITUA": "INT(5) NULL DEFAULT NULL",
        "TYPFAM": "INT(5) NULL DEFAULT NULL",
        "TRAVAILLE": "INT(5) NULL DEFAULT NULL",
        "ETUDIE": "INT(5) NULL DEFAULT NULL",
        "BTRAVTEL": "INT(5) NULL DEFAULT NULL",
        "BTRAVFIX": "INT(5) NULL DEFAULT NULL",
        "BTRAVNBJ": "INT(5) NULL DEFAULT NULL",
        "TEMPTRAV": "INT(5) NULL DEFAULT NULL",
        "dist_ign_trav": "VARCHAR(50) NULL DEFAULT NULL",
        "dist_vo_trav": "VARCHAR(50) NULL DEFAULT NULL",
        "dist_ign_etude": "VARCHAR(50) NULL DEFAULT NULL",
        "dist_vo_etude": "VARCHAR(50) NULL DEFAULT NULL",
        "pond_menC": "VARCHAR(50) NULL DEFAULT NULL",
        "NPERS": "INT(3) NULL DEFAULT NULL",
        "NENFANTS": "INT(3) NULL DEFAULT NULL",
        "TYPMEN15": "INT(3) NULL DEFAULT NULL",
        "quartile_rev": "INT(3) NULL DEFAULT NULL",
        "decile_rev": "INT(3) NULL DEFAULT NULL",
        "COEFFUC": "VARCHAR(10) NULL DEFAULT NULL",
        "quartile_rev_uc": "INT(3) NULL DEFAULT NULL",
        "decile_rev_uc": "INT(3) NULL DEFAULT NULL",
        "TUU2017_RES": "INT(3) NULL DEFAULT NULL",
        "STATUTCOM_UU_RES": "VARCHAR(5) NULL DEFAULT NULL",
        "TAA2017_RES": "INT(3) NULL DEFAULT NULL",
        "CATCOM_AA_RES": "INT(3) NULL DEFAULT NULL",
        "DENSITECOM_RES": "INT(3) NULL DEFAULT NULL",
        "dist_res_tram": "INT(10) NULL DEFAULT NULL",
        "dist_res_metro": "INT(10) NULL DEFAULT NULL",
        "dist_res_train": "INT(10) NULL DEFAULT NULL",
        "dist_res_tgv": "INT(10) NULL DEFAULT NULL",
        "JNBVEH": "INT(3) NULL DEFAULT NULL",
        "JNBVELOAD": "INT(3) NULL DEFAULT NULL",
        "JNBVELOENF": "INT(3) NULL DEFAULT NULL",
        "BLOGDIST": "INT(3) NULL DEFAULT NULL",
        "__csp": "INT(3) NULL DEFAULT NULL",
        "__status": "VARCHAR(50) NULL DEFAULT NULL",
        "__dist_pt": "INT(5) NULL DEFAULT NULL",
        "__main_activity": "VARCHAR(50) NULL DEFAULT NULL",
        "__main_distance": "VARCHAR(50) NULL DEFAULT NULL",
        "__main_transport": "VARCHAR(50) NULL DEFAULT NULL",
        "__work_transport": "VARCHAR(50) NULL DEFAULT NULL",
        "__work_dist": "VARCHAR(50) NULL DEFAULT NULL",
        "__immo_lun": "INT(2) NULL DEFAULT NULL",
        "__immo_mar": "INT(2) NULL DEFAULT NULL",
        "__immo_mer": "INT(2) NULL DEFAULT NULL",
        "__immo_jeu": "INT(2) NULL DEFAULT NULL",
        "__immo_ven": "INT(2) NULL DEFAULT NULL",
        "__immo_sam": "INT(2) NULL DEFAULT NULL",
        "__immo_dim": "INT(2) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (ident_ind) USING BTREE"

    load_database(pool, table_name, persons, cols_table, keys)


def load_emp_travels(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    persons, travels = get_emp()

    cols_table = {
        "IDENT_DEP": "VARCHAR(50) NOT NULL",
        "IDENT_MEN": "VARCHAR(50) NOT NULL",
        "IDENT_IND": "VARCHAR(50) NOT NULL",
        "num_dep": "INT(3) NULL DEFAULT NULL",
        "nb_dep": "INT(3) NULL DEFAULT NULL",
        "POND_JOUR": "VARCHAR(50) NULL DEFAULT NULL",
        "MDATE_jour": "VARCHAR(50) NULL DEFAULT NULL",
        "TYPEJOUR": "INT(2) NULL DEFAULT NULL",
        "MORIHDEP": "VARCHAR(50) NULL DEFAULT NULL",
        "MDESHARR": "VARCHAR(50) NULL DEFAULT NULL",
        "MOTPREC": "VARCHAR(50) NULL DEFAULT NULL",
        "MMOTIFDES": "VARCHAR(50) NULL DEFAULT NULL",
        "DUREE": "INT(10) NULL DEFAULT NULL",
        "mtp": "VARCHAR(50) NULL DEFAULT NULL",
        "MDISTTOT_fin": "VARCHAR(50) NULL DEFAULT NULL",
        "MACCOMPM": "INT(3) NULL DEFAULT NULL",
        "MACCOMPHM": "INT(3) NULL DEFAULT NULL",
        "dist_ign": "VARCHAR(50) NULL DEFAULT NULL",
        "mobloc": "INT(3) NULL DEFAULT NULL",
        "VAC_SCOL": "INT(3) NULL DEFAULT NULL",

    }
    keys = "PRIMARY KEY (IDENT_DEP) USING BTREE, KEY (IDENT_IND) USING BTREE"

    load_database(pool, table_name, travels, cols_table, keys)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 65)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    persons, travels = get_emp()

    security = True
    if not security:
        load_emp_persons(None, "emp_persons")
        load_emp_travels(None, "emp_travels")

