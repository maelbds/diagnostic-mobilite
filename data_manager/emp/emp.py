import pandas as pd

from compute_model.b_survey_association.d_set_matching_attributes import adapt_work_distance
from compute_model.database_connection.db_request import db_request


def get_emp_persons():
    result = db_request(
        """ SELECT emp_persons.ident_ind, ident_men, pond_indC, pond_menC, MDATE_jour, 
                   SEXE, AGE, __csp, __status,
                   NPERS, NENFANTS, JNBVEH,
                   STATUTCOM_UU_RES, TAA2017_RES, CATCOM_AA_RES, DENSITECOM_RES, DEP_RES, 
                   __immo_lun, __immo_mar, __immo_mer,  __immo_jeu,  __immo_ven,
                   __dist_pt,
                   __main_activity, reasons.name, reasons.name_fr,
                   __main_distance,
                   __main_transport, modes.name_fr,
                   __work_transport,
                   __work_dist,
                   travels.vac_scol

            FROM emp_persons

            LEFT JOIN emp_modes ON emp_modes.id_emp = emp_persons.__main_transport
            LEFT JOIN modes_detailed ON emp_modes.id_mode_detailed = modes_detailed.id
            LEFT JOIN modes ON modes_detailed.id_main_mode = modes.id

            LEFT JOIN emp_reasons AS reasons_dict ON emp_persons.__main_activity = reasons_dict.id_emp
            LEFT JOIN reasons ON reasons_dict.id_reason = reasons.id

            LEFT JOIN (SELECT IDENT_IND, MIN(VAC_SCOL) AS vac_scol FROM emp_travels GROUP BY IDENT_IND) AS travels
            ON emp_persons.ident_ind=travels.IDENT_IND
            """, {})

    persons = pd.DataFrame(result, columns=["id_ind", "id_hh", "w_ind", "w_hh", "jour",
                                            "sexe", "age", "csp", "status",
                                            "nb_pers", "nb_child", "nb_car",
                                            "commune_uu_status", "t_aa", "cat_aa", "commune_density", "dep",
                                            "immo_lun", "immo_mar", "immo_mer", "immo_jeu", "immo_ven",
                                            "dist_pt",
                                            "main_activity", "main_activity_name", "main_activity_name_fr",
                                            "main_distance",
                                            "main_transport", "main_transport_name_fr",
                                            "work_transport", "work_dist",
                                            "vac_scol"])
    persons = persons.astype({"w_ind": "float64",
                              "w_hh": "float64",
                              "sexe": "int32",
                              "age": "int32",
                              "csp": "int32",
                              "immo_lun": "int32",
                              "immo_mar": "int32",
                              "immo_mer": "int32",
                              "immo_jeu": "int32",
                              "immo_ven": "int32",
                              "nb_pers": "int32",
                              "nb_child": "int32",
                              "nb_car": "int32",
                              "dist_pt": "float64",
                              "t_aa": "str",
                              "cat_aa": "str",
                              "main_distance": "float64",
                              "work_dist": "float64"})

    # -- SPECIFIC ADJUSTMENT - USED FOR SYNTHETIC POPULATION MATCHING

    # ----- STATUS
    persons["status"] = persons["status"].replace("other_18", "other")

    # ----- CSP
    persons.loc[persons["status"] == "retired", "csp"] = 7

    # ----- CAR NB
    persons.loc[persons["nb_car"] > 2, "nb_car"] = 2

    # ----- DIST PT
    persons["dist_pt"] = persons["dist_pt"].fillna(1000)
    persons["dist_pt"] = persons["dist_pt"].astype("int32")

    # ---- WORK MODE OF TRANSPORT
    def compute_work_transport(row):
        if row["status"] == "employed":
            if row["main_activity"] is None or row["main_transport"] is None:
                return "1"
            if row["main_activity_name_fr"] == "travail":
                mode = row["main_transport_name_fr"]
                if mode == "à pied":
                    return "2"
                elif mode == "vélo":
                    return "3"
                elif mode == "moto":
                    return "4"
                elif mode == "voiture":
                    return "5"
                elif mode == "voiture passager":
                    return "5"
                elif mode == "transport en commun":
                    return "6"
                else:
                    return "1"
            else:
                return "1"
        else:
            return "Z"

    # persons["work_transport"] = persons.apply(lambda row: compute_work_transport(row), axis=1)

    # ---- CHARACTERISTIC DISTANCES
    def compute_activity_distance(row):
        if row["main_activity"] is None or row["main_distance"] is None:
            return [None] * 5
        else:
            reason = row["main_activity_name"]
            dist = str(row["main_distance"])  # str(dist_cat(row["main_distance"]))
            dists = {
                "work": None,
                "education": None,
                "shopping": None,
                "services": None,
                "leisure": None
            }
            if reason in dists.keys():
                dists[reason] = dist
            return dists.values()

    distances = persons.apply(
        lambda x: compute_activity_distance(x), axis=1, result_type='expand').rename(
        columns={0: "work_dist", 1: "education_dist",
                 2: "shopping_dist", 3: "leisure_dist",
                 4: "services_dist"}).astype("float64")
    # persons = pd.merge(persons, distances, left_index=True, right_index=True)

    persons.loc[persons["status"] != "employed", "work_transport"] = "Z"
    persons.loc[persons["status"] != "employed", "work_dist"] = 0
    persons = persons.dropna(subset=["work_transport", "work_dist"])

    persons["vac_scol"] = persons["vac_scol"].fillna(0)
    persons["vac_scol"] = persons["vac_scol"].astype("int32")

    # persons["w_ind"] = persons["w_ind"]*59482366/persons["w_ind"].sum()
    persons["work_dist_adapted"] = persons["work_dist"].apply(adapt_work_distance)

    persons["child/adult"] = persons["nb_child"] / (persons["nb_pers"] - persons["nb_child"])
    persons["child/adult_is1+"] = persons["child/adult"].apply(lambda x: 0 if x < 1 else 1)
    persons["child/adult"] = persons["child/adult"].round(2)

    persons["car/adult"] = persons.apply(
        lambda row: row["nb_car"] / (row["nb_pers"] - row["nb_child"]) if row["nb_pers"] > row["nb_child"] else 0,
        axis=1)
    persons["car/adult_is1+"] = persons["car/adult"].apply(lambda x: min(round(x * 2) / 2, 1))
    persons["car/adult"] = persons["car/adult"].round(2)

    return persons


def get_emp_travels():
    result = db_request(
        """ SELECT IDENT_DEP, IDENT_IND, POND_JOUR,
                    num_dep, nb_dep,
                    TYPEJOUR,
                    MDATE_jour,
                    MORIHDEP, MDESHARR,
                    DUREE,

                    MOTPREC, reasons_ori.name, reasons_ori.name_fr,
                    MMOTIFDES, reasons_des.name, reasons_des.name_fr,

                    mtp, modes.name,  modes.name_fr, 
                    modes_detailed.ghg_emissions_factor, modes_detailed.cost_factor,

                    MDISTTOT_fin,
                    MACCOMPM, MACCOMPHM,
                    
                    TAA2017_ORI, TAA2017_DES,
                    CATCOM_AA_ORI, CATCOM_AA_DES,
                    MEMDESAA,
                    STATUTCOM_UU_ORI, STATUTCOM_UU_DES,
                    DENSITECOM_ORI, DENSITECOM_DES,

                    VAC_SCOL

            FROM emp_travels
            JOIN emp_modes ON emp_modes.id_emp = emp_travels.mtp
            JOIN modes_detailed ON emp_modes.id_mode_detailed = modes_detailed.id
            JOIN modes ON modes_detailed.id_main_mode = modes.id

            JOIN emp_reasons AS reasons_dict_ori ON emp_travels.MOTPREC = reasons_dict_ori.id_emp
            JOIN reasons AS reasons_ori ON reasons_dict_ori.id_reason = reasons_ori.id

            JOIN emp_reasons AS reasons_dict_des ON emp_travels.MMOTIFDES = reasons_dict_des.id_emp
            JOIN reasons AS reasons_des ON reasons_dict_des.id_reason = reasons_des.id

            WHERE mobloc = 1
            """, {})

    travels = pd.DataFrame(result, columns=["id_trav", "id_ind", "w_trav",
                                            "trav_nb", "trav_tot_nb",
                                            "day_type", "day",
                                            "hour_ori", "hour_des", "duration",
                                            "reason_ori", "reason_ori_name", "reason_ori_name_fr",
                                            "reason_des", "reason_des_name", "reason_des_name_fr",
                                            "mode", "mode_name", "mode_name_fr",
                                            "ghg_emissions_factor", "cost_factor",
                                            "distance",
                                            "passengers_hh", "passengers_out_hh",
                                            "tranche_aa_ori", "tranche_aa_des", "cat_aa_ori", "cat_aa_des",
                                            "same_aa_ori_des",
                                            "statut_com_ori", "statut_com_des",
                                            "densite_com_ori", "densite_com_des",
                                            "vac_scol"], dtype=str)

    travels = travels.astype({"w_trav": "float64",
                              "trav_nb": "int32",
                              "trav_tot_nb": "int32",
                              "day_type": "int32",
                              "duration": "int32",
                              "distance": "float64",
                              "ghg_emissions_factor": "float64",
                              "cost_factor": "float64",
                              "passengers_hh": "int32",
                              "passengers_out_hh": "int32"})

    travels["vac_scol"] = travels["vac_scol"].fillna(0)
    travels["vac_scol"] = travels["vac_scol"].astype("int32")

    travels["number"] = 1

    travels["nb_passengers"] = travels["passengers_hh"] + travels["passengers_out_hh"]
    travels.drop(columns=["passengers_hh", "passengers_out_hh"], inplace=True)
    travels["nb_tot_passengers"] = travels["nb_passengers"] + 1

    # out of scolar holidays
    # travels = travels.loc[travels["vac_scol"] == 0]
    # travels["w_trav"] = travels["w_trav"] * 52/36

    # week day only
    travels = travels.loc[travels["day_type"] == 1]
    travels["w_trav"] = travels["w_trav"] / 5

    def group_reason_fr(reasons):
        ori = reasons["reason_ori_name_fr"]
        des = reasons["reason_des_name_fr"]
        if (ori == "domicile" and des == "travail") or (des == "domicile" and ori == "travail"):
            return "domicile ↔ travail"
        elif (ori != "domicile" and des == "travail") or (des != "domicile" and ori == "travail"):
            return "travail ↔ autre"
        elif (ori == "domicile" and des == "études") or (des == "domicile" and ori == "études"):
            return "domicile ↔ études"
        elif (ori == "domicile" and des == "achats") or (des == "domicile" and ori == "achats"):
            return "domicile ↔ achats"
        elif (ori == "domicile" and des == "accompagnement") or (des == "domicile" and ori == "accompagnement"):
            return "domicile ↔ accompagnement"
        elif (ori == "domicile" and des == "loisirs") or (des == "domicile" and ori == "loisirs"):
            return "domicile ↔ loisirs"
        elif (ori == "domicile" and des == "visites") or (des == "domicile" and ori == "visites"):
            return "domicile ↔ visites"
        elif (ori == "domicile" and des == "affaires personnelles") or (
                des == "domicile" and ori == "affaires personnelles"):
            return "domicile ↔ affaires personnelles"
        else:
            return "autre"

    travels["reason_name_fr"] = travels[["reason_ori_name_fr", "reason_des_name_fr"]].apply(
        lambda r: group_reason_fr(r), axis=1)

    return travels


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)
    persons = get_emp_persons()
    travels = get_emp_travels()
    print(persons)
    print(travels)


    modes_nb = travels.groupby("reason_name_fr")["w_trav"].sum().round()
    modes_dist = travels.groupby("reason_name_fr") \
        .apply(lambda df: (df["w_trav"] * df["distance"]).sum().round())
    modes_significance = travels.groupby("reason_name_fr") \
        .apply(lambda df: df["id_ind"].drop_duplicates().count())
    modes = pd.DataFrame({"nombre - %": (modes_nb / modes_nb.sum() * 100).round(1),
                          "distance - %": (modes_dist / modes_dist.sum() * 100).round(1),
                          "effectif": modes_significance})

    print(modes)




