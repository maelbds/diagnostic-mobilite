import pandas as pd
import numpy as np

from data_manager.dictionnary.reasons import get_reasons
from data_manager.entd.distribute_work_distances import find_distances
from data_manager.entd.entd_modes import get_entd_modes
from data_manager.entd.entd_reasons import get_entd_reasons

ENTD_CATEGORIES = get_entd_reasons("2018").rename(columns={"id_entd": "motif", "id_reason": "reason_id"}).set_index(
    "motif")

reasons = get_reasons(None)
REASONS_RANK = {id_r: {"name": name,
                       "rank": rank} for id_r, name, rank in zip(reasons["id"],
                                                                 reasons["name"],
                                                                 reasons["rank_main_activity"])}
ENTD_MODES = get_entd_modes("2018")
# dedicated changes to fit with work_transport
ENTD_MODES.loc[ENTD_MODES["id_entd"]=="1.2","name_mode"] = "walk"
ENTD_MODES.loc[ENTD_MODES["id_entd"]=="1.3","name_mode"] = "walk"
ENTD_MODES.loc[ENTD_MODES["id_entd"]=="1.4","name_mode"] = "walk"
ENTD_MODES.loc[ENTD_MODES["id_entd"]=="4.1","name_mode"] = "car"
ENTD_MODES.loc[ENTD_MODES["id_entd"]=="4.2","name_mode"] = "car"
ENTD_MODES.loc[ENTD_MODES["id_entd"]=="5.2","name_mode"] = "public transport"


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
    reasons = [ENTD_CATEGORIES.loc[motif, "reason_id"] for motif in motifs]
    reasons_rank = [REASONS_RANK[r]["rank"] for r in reasons]
    main_reason = motifs[reasons_rank.index(min(reasons_rank))]
    return main_reason


def get_work_transport_dist(persons, travels):
    # manage modes to INSEE work transport categories
    def compute_work_transport(wt):
        if wt == 1:
            return 1
        else:
            if wt is None:
                return None
            else:
                mode = None
                if len(ENTD_MODES.loc[ENTD_MODES["id_entd"] == wt, "name_mode"]) > 0:
                    mode = ENTD_MODES.loc[ENTD_MODES["id_entd"] == wt, "name_mode"].iloc[0]
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
    print(persons_sources_Z)
    distances, modes = find_distances(persons_to_look_for_similar_profiles, persons_sources)

    print(distances)

    persons.loc[mask_persons_employed & ~mask_persons_work_home & ~mask_main_activity_work & ~mask_main_activity_isna, "__work_transport"] = modes
    persons.loc[mask_persons_employed & ~mask_persons_work_home & ~mask_main_activity_work & ~mask_main_activity_isna, "__work_dist"] = distances

    mask_transport_Z = persons["__work_transport"] == "Z"
    print(persons[mask_transport_Z & mask_persons_employed & ~mask_persons_work_home & ~mask_main_activity_work & ~mask_main_activity_isna])
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
    print(persons[mask_transport_Z & mask_persons_employed & ~mask_persons_work_home & mask_main_activity_isna])

    print(persons)
    return persons


def get_chained_work_dist(persons, travels):

    mask_persons_employed = persons["__status"] == "employed"
    # case of persons working home
    mask_persons_work_home = persons["BTRAVFIX"] == "5"
    # case of persons working away from home
    mask_main_activity_work = persons["__main_activity"].isin(["9.1", "9.2", "9.3", "9.4", "9.5"])
    mask_main_activity_isna = persons["__main_activity"].isna()

    print("BEFORE")
    print(persons[mask_persons_employed]["pond_indC"].sum())
    print(persons[mask_persons_employed & mask_persons_work_home]["pond_indC"].sum())
    print(persons[mask_persons_employed & ~mask_persons_work_home]["pond_indC"].sum())
    print(persons[mask_persons_employed & ~mask_persons_work_home & mask_main_activity_work]["pond_indC"].sum())
    print(persons[mask_persons_employed & ~mask_persons_work_home & ~mask_main_activity_work & mask_main_activity_isna]["pond_indC"].sum())
    print(persons[mask_persons_employed & ~mask_persons_work_home & ~mask_main_activity_work & ~mask_main_activity_isna]["pond_indC"].sum())


    travels.loc[:, "MDISTTOT_fin"] = travels.loc[:, "MDISTTOT_fin"].astype(float)
    travels.loc[:, "num_dep"] = travels.loc[:, "num_dep"].astype(float)

    mask_travels_persons_employed = travels["IDENT_IND"].isin(persons.loc[mask_persons_employed, "ident_ind"])
    travels_emp = travels[mask_travels_persons_employed].copy()
    travels_emp = travels_emp.sort_values(["IDENT_IND", "num_dep"])
    print(travels_emp)

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
    print(travels_emp)

    travels_emp["marker_ori"] = travels_emp["home_marker_ori"] + travels_emp["work_marker_ori"]
    travels_emp["home_work_path"] = travels_emp[["IDENT_IND", "marker_ori"]].groupby("IDENT_IND", as_index=False).cumsum()

    travels_emp_path = travels_emp[["IDENT_IND", "home_work_path", "home_marker_ori", "work_marker_ori", "home_marker_des", "work_marker_des", "MDISTTOT_fin", "count"]].groupby(by=["IDENT_IND", "home_work_path"], as_index=False).sum()
    print(travels_emp_path)
    travels_emp_path["marker_work_home"] = travels_emp_path["home_marker_des"] + travels_emp_path["work_marker_ori"]
    travels_emp_path["marker_home_work"] = travels_emp_path["home_marker_ori"] + travels_emp_path["work_marker_des"]
    travels_emp_path_home_work_chained = travels_emp_path[(travels_emp_path["marker_work_home"] == 2) | (travels_emp_path["marker_home_work"] == 2)]
    print(travels_emp_path_home_work_chained)

    travels_emp_path_home_work_chained_dist = travels_emp_path_home_work_chained[["IDENT_IND", "MDISTTOT_fin"]].groupby("IDENT_IND", as_index=False).min().rename(columns={"MDISTTOT_fin": "new_work_dist"})
    print(travels_emp_path_home_work_chained_dist)

    persons_with_chained_work_dist = pd.merge(persons, travels_emp_path_home_work_chained_dist, left_on="ident_ind", right_on="IDENT_IND", how="left")
    persons_with_chained_work_dist = persons_with_chained_work_dist.drop(columns=["IDENT_IND"])
    print(persons_with_chained_work_dist)

    # add new dist and activity only for eligible people
    mask_new_dist = ~persons_with_chained_work_dist["new_work_dist"].isna()
    mask_eligible = mask_persons_employed & ~mask_persons_work_home & ~mask_main_activity_work & mask_new_dist

    print(mask_eligible)
    print(persons[mask_eligible])
    print(persons[mask_eligible]["pond_indC"].sum())
    print(persons_with_chained_work_dist[mask_eligible])

    persons.loc[mask_eligible, "__main_activity"] = "9.1"
    persons.loc[mask_eligible, "__main_distance"] = persons_with_chained_work_dist.loc[mask_eligible, "new_work_dist"]
    #persons.loc[mask_eligible, "__work_dist"] = persons_with_chained_work_dist.loc[mask_eligible, "new_work_dist"]
    #persons.loc[mask_eligible, "__work_transport"] = persons_with_chained_work_dist.loc[mask_eligible, "__main_transport"]

    print(persons[mask_eligible])

    mask_persons_employed = persons["__status"] == "employed"
    # case of persons working home
    mask_persons_work_home = persons["BTRAVFIX"] == "5"
    # case of persons working away from home
    mask_main_activity_work = persons["__main_activity"].isin(["9.1", "9.2", "9.3", "9.4", "9.5"])
    mask_main_activity_isna = persons["__main_activity"].isna()

    print("AFTER")
    print(persons[mask_persons_employed]["pond_indC"].sum())
    print(persons[mask_persons_employed & mask_persons_work_home]["pond_indC"].sum())
    print(persons[mask_persons_employed & ~mask_persons_work_home]["pond_indC"].sum())
    print(persons[mask_persons_employed & ~mask_persons_work_home & mask_main_activity_work]["pond_indC"].sum())
    print(persons[mask_persons_employed & ~mask_persons_work_home & ~mask_main_activity_work & mask_main_activity_isna]["pond_indC"].sum())
    print(persons[mask_persons_employed & ~mask_persons_work_home & ~mask_main_activity_work & ~mask_main_activity_isna]["pond_indC"].sum())


    print(persons)
    return persons


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    print(ENTD_CATEGORIES)
    print(REASONS_RANK)
