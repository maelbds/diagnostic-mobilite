"""
To load ENTD survey data from csv to database | EXECUTE ONCE
"""
import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection

from data_manager.entd.find_main_activity_2018 import get_main_activity_and_dist, get_work_transport_dist, \
    get_chained_work_dist
from data_manager.entd.clean_prepare_entd_2018 import create_status, clean_persons_with_hh, \
    create_csp, create_dist_pt, clean_travels, create_day_type, create_immo_days

pd.set_option('display.max_columns', 65)
pd.set_option('display.max_rows', 50)
pd.set_option('display.width', 2000)


def save_persons_data_from_csv_to_db(persons):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in persons.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in persons.columns]) + ")"
    persons = persons.replace({np.nan: None})

    def request(cur, cols):
        cur.execute("""INSERT INTO entd_persons_2018 """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in persons.iterrows()]

    conn.commit()
    conn.close()


def save_travels_data_from_csv_to_db(travels):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in travels.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in travels.columns]) + ")"
    travels = travels.replace({np.nan: None})

    def request(cur, cols):
        cur.execute("""INSERT INTO entd_travels_2018 """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in travels.iterrows()]

    conn.commit()
    conn.close()


def read_csv(file_name, variables_name):
    variables = pd.read_csv(
        "data/2018/variables.csv",
        sep=";", dtype=str)
    cols = variables[variables_name].dropna().apply(lambda x: x.upper()).tolist()
    data = pd.read_csv(file_name, sep=";", dtype=str,
                       usecols=lambda x: x.upper() in cols, encoding="ansi")
    return data


# HOUSEHOLDS
tcm_menage = read_csv(
    "data/2018/tcm_men_public.csv",
    "TCM_MEN"
)
q_menage = read_csv(
    "data/2018/q_menage_public.csv",
    "Q_MENAGE"
)
households = pd.merge(tcm_menage, q_menage, left_on="ident_men", right_on="IDENT_MEN").drop(columns=["IDENT_MEN"])

# PEOPLE
tcm_ind_kish = read_csv(
    "data/2018/tcm_ind_kish_public.csv",
    "TCM_IND_KISH_public"
)
k_individu = read_csv(
    "data/2018/k_individu_public.csv",
    "K_INDIVIDU"
)
persons = pd.merge(tcm_ind_kish, k_individu, left_on="ident_ind", right_on="IDENT_IND").drop(columns=["IDENT_IND"])

# COMBINED
persons_with_hh = pd.merge(persons, households, left_on="ident_men", right_on="ident_men")

# CLEANING DATA
persons_with_hh = clean_persons_with_hh(persons_with_hh)

# COMPUTE VARIABLES
persons_with_hh = create_csp(persons_with_hh)
persons_with_hh = create_day_type(persons_with_hh)
persons_with_hh = create_status(persons_with_hh)
persons_with_hh = create_dist_pt(persons_with_hh)
persons_with_hh = create_immo_days(persons_with_hh)

# TRAVELS
travels = read_csv(
    "data/2018/k_deploc_public.csv",
    "K_DEPLOC"
)

# CLEANING DATA
travels = clean_travels(travels)

# INDICATORS
persons["pond_indC"] = persons["pond_indC"].astype("float64")
print("PERSONS")
print(persons)
print(f"Population totale représentée {persons['pond_indC'].sum().round()}")
print("TRAVELS")
print(travels)
travels_with_persons = pd.merge(travels, persons, left_on="IDENT_IND", right_on="ident_ind")
print(f"Population totale représentée ayant recensé des déplacements {travels_with_persons.drop_duplicates(subset='IDENT_IND')['pond_indC'].sum().round()}")
print(f"Nombre total de déplacements {travels_with_persons['pond_indC'].sum().round()}")


# CREATE MAIN ACTIVITY AND DIST
persons_with_hh_and_activities = get_main_activity_and_dist(persons_with_hh, travels)

# COMPUTE CHAINED WORK DIST FOR EMPLOYED PEOPLE
persons_with_hh_and_activities = get_chained_work_dist(persons_with_hh_and_activities, travels)

# CREATE WORK_TRANSPORT & WORK_DIST
persons_with_hh_and_activities = get_work_transport_dist(persons_with_hh_and_activities, travels)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":

    print(persons_with_hh_and_activities)
    print(travels)

    travels_with_persons = pd.merge(travels, persons_with_hh_and_activities, left_on="IDENT_IND", right_on="ident_ind")
    print(travels_with_persons)

    print("  CHECK DISTANCE REPARTITION OF MATCHED work_dist")

    mask_persons_employed = persons_with_hh_and_activities["__status"] == "employed"
    mask_persons_work_home = persons_with_hh_and_activities["BTRAVFIX"] == "5"
    mask_main_activity_work = persons_with_hh_and_activities["__main_activity"].isin(["9.1", "9.2", "9.3", "9.5", "9.5"])
    mask_main_activity_isna = persons_with_hh_and_activities["__main_activity"].isna()
    mask_main_mode_isna = persons_with_hh_and_activities["__main_transport"].isna()
    mask_main_dist_isna = persons_with_hh_and_activities["__main_distance"].isna()

    persons_matched = persons_with_hh_and_activities.loc[mask_persons_employed & ~mask_persons_work_home & ~mask_main_activity_work]
    persons_sources = persons_with_hh_and_activities.loc[mask_persons_employed & ~mask_persons_work_home & mask_main_activity_work]

    print("-- sources")
    persons_a = persons_sources[["pond_indC", "__work_dist", "__work_transport", "__csp"]]
    persons_a = persons_a.fillna(-10)
    persons_a = persons_a.astype({"pond_indC": "float64", "__work_dist": "float64"})
    persons_a["__work_dist_cat"] = np.floor(persons_a["__work_dist"]/10)*10
    persons_a["__work_dist_cat1"] = np.floor(persons_a["__work_dist"])
    mask_walk = persons_a["__work_transport"] == "2"
    mask_tc = persons_a["__work_transport"] == "6"
    print(persons_a.groupby("__work_dist_cat").sum())
    print((persons_a.groupby("__work_dist_cat").sum()/persons_a["pond_indC"].sum()*100).round(1))
    print(persons_a.groupby("__work_transport").sum())
    print((persons_a.groupby("__work_transport").sum()/persons_a["pond_indC"].sum()*100).round(1))
    print(persons_a.groupby("__csp").sum())
    print((persons_a.groupby("__csp").sum()/persons_a["pond_indC"].sum()*100).round(1))
    print("walk")
    print(persons_a[mask_walk].groupby("__work_dist_cat").sum())
    print((persons_a[mask_walk].groupby("__work_dist_cat").sum()/persons_a[mask_walk]["pond_indC"].sum()*100).round(1))
    print(persons_a[mask_walk].groupby("__work_dist_cat1").sum())
    print((persons_a[mask_walk].groupby("__work_dist_cat1").sum()/persons_a[mask_walk]["pond_indC"].sum()*100).round(1))
    print("public transport")
    print(persons_a[mask_tc].groupby("__work_dist_cat").sum())
    print((persons_a[mask_tc].groupby("__work_dist_cat").sum()/persons_a[mask_tc]["pond_indC"].sum()*100).round(1))


    print("-- matched")
    persons_b = persons_matched[["pond_indC", "__work_dist", "__work_transport", "__csp"]]
    persons_b = persons_b.fillna(-10)
    persons_b = persons_b.astype({"pond_indC": "float64", "__work_dist": "float64"})
    persons_b["__work_dist_cat"] = np.floor(persons_b["__work_dist"]/10)*10
    persons_b["__work_dist_cat1"] = np.floor(persons_b["__work_dist"])
    mask_walk = persons_b["__work_transport"] == "2"
    mask_tc = persons_b["__work_transport"] == "6"
    print(persons_b.groupby("__work_dist_cat").sum())
    print((persons_b.groupby("__work_dist_cat").sum()/persons_b["pond_indC"].sum()*100).round(1))
    print(persons_b.groupby("__work_transport").sum())
    print((persons_b.groupby("__work_transport").sum()/persons_b["pond_indC"].sum()*100).round(1))
    print(persons_b.groupby("__csp").sum())
    print((persons_b.groupby("__csp").sum()/persons_b["pond_indC"].sum()*100).round(1))
    print("walk")
    print(persons_b[mask_walk].groupby("__work_dist_cat").sum())
    print((persons_b[mask_walk].groupby("__work_dist_cat").sum()/persons_b[mask_walk]["pond_indC"].sum()*100).round(1))
    print(persons_b[mask_walk].groupby("__work_dist_cat1").sum())
    print((persons_b[mask_walk].groupby("__work_dist_cat1").sum()/persons_b[mask_walk]["pond_indC"].sum()*100).round(1))
    print("public transport")
    print(persons_b[mask_tc].groupby("__work_dist_cat").sum())
    print((persons_b[mask_tc].groupby("__work_dist_cat").sum()/persons_b[mask_tc]["pond_indC"].sum()*100).round(1))


    print("Persons employed without work transport & work dist")
    mask_no_work_transport = persons_with_hh_and_activities["__work_transport"].isna()
    mask_no_work_dist = persons_with_hh_and_activities["__work_dist"].isna()
    print("-- without work transport")
    print(persons_with_hh_and_activities.loc[mask_persons_employed & mask_no_work_transport])
    print(persons_with_hh_and_activities.loc[mask_persons_employed & mask_no_work_transport, "pond_indC"].sum())
    print("-- without work dist")
    print(persons_with_hh_and_activities.loc[mask_persons_employed & mask_no_work_dist])
    print(persons_with_hh_and_activities.loc[mask_persons_employed & mask_no_work_dist, "pond_indC"].sum())

    print(persons_with_hh_and_activities.loc[mask_persons_employed, ["pond_indC", "__work_transport"]].groupby("__work_transport").sum()/persons_with_hh_and_activities.loc[mask_persons_employed, "pond_indC"].sum())
    mask_transport_Z = persons_with_hh_and_activities["__work_transport"] == "Z"
    print(persons_with_hh_and_activities[mask_persons_employed & mask_transport_Z])

    # to prevent from unuseful loading data
    security = True
    if not security:
        print("saving")
        #save_persons_data_from_csv_to_db(persons_with_hh_and_activities)
        #save_travels_data_from_csv_to_db(travels)
