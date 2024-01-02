import pandas as pd
import numpy as np

from compute_model.v_database_connection.db_request import db_request
from data_manager.emp.distribute_work_distances import find_distances


def get_emp_modes():
    result = db_request("""
        SELECT emp_modes.id_emp, modes.id, modes.name 
        FROM emp_modes
        LEFT JOIN modes_detailed ON emp_modes.id_mode_detailed = modes_detailed.id
        LEFT JOIN modes ON modes_detailed.id_main_mode = modes.id
    """, {})
    emp_modes = pd.DataFrame(result, columns=["id_entd", "id_mode", "name_mode"])
    # dedicated changes to fit with work_transport
    emp_modes.loc[emp_modes["id_entd"]=="1.2", "name_mode"] = "walk"
    emp_modes.loc[emp_modes["id_entd"]=="1.3", "name_mode"] = "walk"
    emp_modes.loc[emp_modes["id_entd"]=="1.4", "name_mode"] = "walk"
    emp_modes.loc[emp_modes["id_entd"]=="4.1", "name_mode"] = "car"
    emp_modes.loc[emp_modes["id_entd"]=="4.2", "name_mode"] = "car"
    emp_modes.loc[emp_modes["id_entd"]=="5.2", "name_mode"] = "public transport"
    return emp_modes


def get_emp_categories():
    result = db_request("""
        SELECT id_emp, name_emp, id_reason 
        FROM emp_reasons
    """, {})
    emp_categories = pd.DataFrame(result, columns=["motif", "name_entd", "reason_id"]).set_index("motif")
    return emp_categories


def get_reasons():
    result = db_request("""
        SELECT * FROM reasons
    """, {})
    reasons = pd.DataFrame(result, columns=["id", "name", "name_fr", "rank_main_activity"])

    reasons = {id_r: {"name": name,
                           "rank": rank} for id_r, name, rank in zip(reasons["id"],
                                                                     reasons["name"],
                                                                     reasons["rank_main_activity"])}
    return reasons


def get_main_activity_and_dist(persons, travels):
    travels.loc[:, "MDISTTOT_fin"] = travels.loc[:, "MDISTTOT_fin"].astype(float)

    def add_activity_dist_transport(ind_id, travel):
        activity, distance, transport = find_main_activity_distance_transport(travel)
        persons.loc[persons.loc[:, "ident_ind"] == ind_id, "__main_activity"] = activity
        persons.loc[persons.loc[:, "ident_ind"] == ind_id, "__main_distance"] = distance
        persons.loc[persons.loc[:, "ident_ind"] == ind_id, "__main_transport"] = transport

    [add_activity_dist_transport(ind_id, ind_travel) for ind_id, ind_travel in travels.groupby("IDENT_IND")]

    # USING DIST IGN WORK/STUDY IF AVAILABLE
    mask_work_activity = persons["dist_ign_trav"].notna()
    mask_study_activity = persons["dist_ign_etude"].notna()
    persons.loc[mask_work_activity, "__main_activity"] = "9.1"
    persons.loc[mask_work_activity, "__main_distance"] = persons.loc[mask_work_activity, "dist_ign_trav"]
    persons.loc[mask_study_activity, "__main_activity"] = "1.4"
    persons.loc[mask_study_activity, "__main_distance"] = persons.loc[mask_study_activity, "dist_ign_etude"]

    return persons


def find_main_activity_distance_transport(travels):
    home_travels = travels[(travels["MMOTIFDES"] == "1.1") | (travels["MOTPREC"] == "1.1")]
    if len(home_travels.index) == 0:
        return None, None, None
    reasons = home_travels.loc[:, "MMOTIFDES"].to_list() + home_travels.loc[:, "MOTPREC"].to_list()
    main_reason = find_main_reason(reasons)
    distances = home_travels.loc[(home_travels.loc[:, "MOTPREC"] == main_reason) |
                                 (home_travels.loc[:, "MMOTIFDES"] == main_reason), "MDISTTOT_fin"]

    main_distance = min(distances)
    transports = home_travels.loc[(home_travels.loc[:, "MOTPREC"] == main_reason) |
                                  (home_travels.loc[:, "MMOTIFDES"] == main_reason), "mtp"]
    main_transport = transports.mode().iloc[0]

    return main_reason, main_distance, main_transport


def find_main_reason(motifs):
    emp_categories = get_emp_categories()
    REASONS_RANK = get_reasons()
    reasons = [emp_categories.loc[motif, "reason_id"] for motif in motifs]
    reasons_rank = [REASONS_RANK[r]["rank"] for r in reasons]
    main_reason = motifs[reasons_rank.index(min(reasons_rank))]
    return main_reason


def get_work_transport_dist(persons, travels):
    emp_modes = get_emp_modes()
    # manage modes to INSEE work transport categories
    def compute_work_transport(wt):
        if wt == 1:
            return 1
        else:
            if wt is None:
                return None
            else:
                mode = None
                if len(emp_modes.loc[emp_modes["id_entd"] == wt, "name_mode"]) > 0:
                    mode = emp_modes.loc[emp_modes["id_entd"] == wt, "name_mode"].iloc[0]
                if mode == "walk":
                    return "2"
                elif mode == "bike":
                    return "3"
                elif mode == "motorbike":
                    return "4"
                elif mode == "car":
                    return "5"
                elif mode == "car passenger":
                    return "5"
                elif mode == "public transport":
                    return "6"
                else:
                    return None

    # in this function we set transport mode & distance for work travels, then only for employed people
    mask_persons_employed = persons["__status"] == "employed"

    # case of persons working home
    mask_persons_work_home = persons["BTRAVFIX"] == "5"
    persons.loc[mask_persons_employed & mask_persons_work_home, "__work_transport"] = "1"
    persons.loc[mask_persons_employed & mask_persons_work_home, "__work_dist"] = 0

    # case of persons working away from home
    mask_main_activity_work = persons["__main_activity"].isin(["9.1", "9.2", "9.3", "9.4", "9.5"])
    mask_main_activity_isna = persons["__main_activity"].isna()

    #   case of persons with main_activity == work
    #   - we use the associated transport and dist as work transport and dist
    persons.loc[mask_persons_employed & ~mask_persons_work_home & mask_main_activity_work, "__work_transport"] = persons.loc[mask_persons_employed & ~mask_persons_work_home & mask_main_activity_work, "__main_transport"].apply(lambda x: compute_work_transport(x))
    persons.loc[mask_persons_employed & ~mask_persons_work_home & mask_main_activity_work, "__work_dist"] = persons.loc[mask_persons_employed & ~mask_persons_work_home & mask_main_activity_work, "__main_distance"]

    #   case of persons with main_activity != work & not na
    #   - we assign work transport based on transport of main_activity
    #   - we assign distance based on the distance distribution of similar profiles
    #persons.loc[mask_persons_employed & ~mask_persons_work_home & ~mask_main_activity_work & ~mask_main_activity_isna, "__work_transport"] = persons.loc[mask_persons_employed & ~mask_persons_work_home & ~mask_main_activity_work & ~mask_main_activity_isna, "__main_transport"].apply(lambda x: compute_work_transport(x))

    mask_transport_Z = persons["__work_transport"] == "Z"
    persons_to_look_for_similar_profiles = persons.loc[mask_persons_employed & ~mask_persons_work_home & ~mask_main_activity_work & ~mask_main_activity_isna]
    persons_sources = persons.loc[mask_persons_employed & ~mask_persons_work_home & mask_main_activity_work]
    persons_sources_Z = persons.loc[mask_persons_employed & ~mask_persons_work_home & mask_main_activity_work & mask_transport_Z]
    distances, modes = find_distances(persons_to_look_for_similar_profiles, persons_sources)


    persons.loc[mask_persons_employed & ~mask_persons_work_home & ~mask_main_activity_work & ~mask_main_activity_isna, "__work_transport"] = modes
    persons.loc[mask_persons_employed & ~mask_persons_work_home & ~mask_main_activity_work & ~mask_main_activity_isna, "__work_dist"] = distances

    mask_transport_Z = persons["__work_transport"] == "Z"
    #   case of persons with main_activity is na
    #   - we set None & won't use them
    #persons.loc[mask_persons_employed & ~mask_persons_work_home & mask_main_activity_isna, "__work_transport"] = None
    #persons.loc[mask_persons_employed & ~mask_persons_work_home & mask_main_activity_isna, "__work_dist"] = None

    persons_to_look_for_similar_profiles = persons.loc[mask_persons_employed & ~mask_persons_work_home & mask_main_activity_isna]
    persons_sources = persons.loc[mask_persons_employed & ~mask_persons_work_home & mask_main_activity_work]
    distances, modes = find_distances(persons_to_look_for_similar_profiles, persons_sources)

    persons.loc[mask_persons_employed & ~mask_persons_work_home & mask_main_activity_isna, "__work_transport"] = modes
    persons.loc[mask_persons_employed & ~mask_persons_work_home & mask_main_activity_isna, "__work_dist"] = distances

    mask_transport_Z = persons["__work_transport"] == "Z"

    return persons


def get_chained_work_dist(persons, travels):

    mask_persons_employed = persons["__status"] == "employed"
    # case of persons working home
    mask_persons_work_home = persons["BTRAVFIX"] == "5"
    # case of persons working away from home
    mask_main_activity_work = persons["__main_activity"].isin(["9.1", "9.2", "9.3", "9.4", "9.5"])
    mask_main_activity_isna = persons["__main_activity"].isna()

    travels.loc[:, "MDISTTOT_fin"] = travels.loc[:, "MDISTTOT_fin"].astype(float)
    travels.loc[:, "num_dep"] = travels.loc[:, "num_dep"].astype(float)

    mask_travels_persons_employed = travels["IDENT_IND"].isin(persons.loc[mask_persons_employed, "ident_ind"])
    travels_emp = travels[mask_travels_persons_employed].copy()
    travels_emp = travels_emp.sort_values(["IDENT_IND", "num_dep"])

    mask_home_ori = travels_emp["MOTPREC"] == "1.1"
    travels_emp.loc[mask_home_ori, "home_marker_ori"] = 1
    travels_emp.loc[~mask_home_ori, "home_marker_ori"] = 0
    mask_home_des = travels_emp["MMOTIFDES"] == "1.1"
    travels_emp.loc[mask_home_des, "home_marker_des"] = 1
    travels_emp.loc[~mask_home_des, "home_marker_des"] = 0

    mask_work_ori = travels_emp["MOTPREC"].isin(["9.1", "9.2", "9.3", "9.4", "9.5"])
    travels_emp.loc[mask_work_ori, "work_marker_ori"] = 1
    travels_emp.loc[~mask_work_ori, "work_marker_ori"] = 0
    mask_work_des = travels_emp["MMOTIFDES"].isin(["9.1", "9.2", "9.3", "9.4", "9.5"])
    travels_emp.loc[mask_work_des, "work_marker_des"] = 1
    travels_emp.loc[~mask_work_des, "work_marker_des"] = 0

    travels_emp["count"] = 1

    travels_emp["marker_ori"] = travels_emp["home_marker_ori"] + travels_emp["work_marker_ori"]
    travels_emp["home_work_path"] = travels_emp[["IDENT_IND", "marker_ori"]].groupby("IDENT_IND", as_index=False).cumsum()

    travels_emp_path = travels_emp[["IDENT_IND", "home_work_path", "home_marker_ori", "work_marker_ori", "home_marker_des", "work_marker_des", "MDISTTOT_fin", "count"]].groupby(by=["IDENT_IND", "home_work_path"], as_index=False).sum()
    travels_emp_path["marker_work_home"] = travels_emp_path["home_marker_des"] + travels_emp_path["work_marker_ori"]
    travels_emp_path["marker_home_work"] = travels_emp_path["home_marker_ori"] + travels_emp_path["work_marker_des"]
    travels_emp_path_home_work_chained = travels_emp_path[(travels_emp_path["marker_work_home"] == 2) | (travels_emp_path["marker_home_work"] == 2)]

    travels_emp_path_home_work_chained_dist = travels_emp_path_home_work_chained[["IDENT_IND", "MDISTTOT_fin"]].groupby("IDENT_IND", as_index=False).min().rename(columns={"MDISTTOT_fin": "new_work_dist"})

    persons_with_chained_work_dist = pd.merge(persons, travels_emp_path_home_work_chained_dist, left_on="ident_ind", right_on="IDENT_IND", how="left")
    persons_with_chained_work_dist = persons_with_chained_work_dist.drop(columns=["IDENT_IND"])

    # add new dist and activity only for eligible people
    mask_new_dist = ~persons_with_chained_work_dist["new_work_dist"].isna()
    mask_eligible = mask_persons_employed & ~mask_persons_work_home & ~mask_main_activity_work & mask_new_dist

    persons.loc[mask_eligible, "__main_activity"] = "9.1"
    persons.loc[mask_eligible, "__main_distance"] = persons_with_chained_work_dist.loc[mask_eligible, "new_work_dist"]
    #persons.loc[mask_eligible, "__work_dist"] = persons_with_chained_work_dist.loc[mask_eligible, "new_work_dist"]
    #persons.loc[mask_eligible, "__work_transport"] = persons_with_chained_work_dist.loc[mask_eligible, "__main_transport"]

    mask_persons_employed = persons["__status"] == "employed"
    # case of persons working home
    mask_persons_work_home = persons["BTRAVFIX"] == "5"
    # case of persons working away from home
    mask_main_activity_work = persons["__main_activity"].isin(["9.1", "9.2", "9.3", "9.4", "9.5"])
    mask_main_activity_isna = persons["__main_activity"].isna()

    return persons


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    print(get_emp_modes())
    print(get_emp_categories())
    print(get_reasons())
