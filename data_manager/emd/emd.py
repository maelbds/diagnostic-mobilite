import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection, mariadb_connection_pool
from data_manager.entd_emd.analysis import analysis
from data_manager.entd_emd.standardisation import standard_specific_emd, standard_indicators, standard_reason
from data_manager.insee_general.districts import geo_codes_city_to_district


def standard_emd(pool, persons, travels, year):
    persons, travels = standard_specific_emd(pool, persons, travels, year)
    travels = standard_indicators(travels)
    travels = standard_reason(travels)
    return persons, travels


def get_emd_by_id(pool, emd_id):
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    cur.execute("""SELECT 
                   emd_name, emd_year
                   FROM emd_datasets
                   WHERE emd_id = ?""", [emd_id])
    result = list(cur)
    emd_ids = pd.DataFrame(result, columns=["emd_name", "emd_year"])
    emd_name = emd_ids["emd_name"].iloc[0]
    emd_year = emd_ids["emd_year"].iloc[0]

    cur.execute("""SELECT 
                   id_ind, id_hh, w_ind, ra_id, emd_geo.geo_code, sexe, age, status, csp, nb_car, day
                   FROM emd_persons
                   LEFT JOIN emd_geo ON emd_persons.ra_id = emd_geo.id AND emd_persons.emd_id = emd_geo.emd_id
                   WHERE emd_persons.emd_id = ? """, [emd_id])
    result = list(cur)
    persons = pd.DataFrame(result,
                           columns=["id_ind", "id_hh", "w_ind", "ra_id", "geo_code", "sexe",
                                    "age", "status", "csp", "nb_car", "day"])

    cur.execute("""SELECT 
                   id_ind, id_trav, trav_nb, emd_travels.reason_ori, reasons_ori.name, reasons_ori.name_fr, zone_ori, emd_geo_ori.geo_code, hour_ori, 
                   emd_travels.reason_des, reasons_des.name, reasons_des.name_fr, zone_des, emd_geo_des.geo_code, hour_des, duration, modp, modes.name_fr, distance,
                   modes_detailed.ghg_emissions_factor, modes_detailed.cost_factor
                   FROM emd_travels
                   
                   JOIN emd_modes_dict ON emd_travels.modp = emd_modes_dict.value AND emd_travels.emd_id = emd_modes_dict.emd_id
                   JOIN modes_detailed ON emd_modes_dict.mode_id = modes_detailed.id
                   JOIN modes ON modes_detailed.id_main_mode = modes.id
                   
                   JOIN emd_reasons_dict AS reasons_dict_ori ON emd_travels.reason_ori = reasons_dict_ori.value AND emd_travels.emd_id = reasons_dict_ori.emd_id
                   JOIN emd_reasons AS emd_reasons_ori ON reasons_dict_ori.reason_id = emd_reasons_ori.id
                   JOIN reasons AS reasons_ori ON emd_reasons_ori.id_main_reason = reasons_ori.id
                   
                   JOIN emd_reasons_dict AS reasons_dict_des ON emd_travels.reason_des = reasons_dict_des.value AND emd_travels.emd_id = reasons_dict_des.emd_id
                   JOIN emd_reasons AS emd_reasons_des ON reasons_dict_des.reason_id = emd_reasons_des.id
                   JOIN reasons AS reasons_des ON emd_reasons_des.id_main_reason = reasons_des.id 
                   
                   LEFT JOIN emd_geo AS emd_geo_ori ON emd_travels.zone_ori = emd_geo_ori.id AND emd_travels.emd_id = emd_geo_ori.emd_id
                   LEFT JOIN emd_geo AS emd_geo_des ON emd_travels.zone_des = emd_geo_des.id AND emd_travels.emd_id = emd_geo_des.emd_id
                   WHERE emd_travels.emd_id = ? """, [emd_id])
    result = list(cur)
    travels = pd.DataFrame(result,
                           columns=["id_ind", "id_trav", "trav_nb", "reason_ori", "reason_ori_name", "reason_ori_name_fr", "id_ori",
                                    "c_geo_code_ori", "hour_ori",
                                    "reason_des", "reason_des_name", "reason_des_name_fr", "id_des", "c_geo_code_des", "hour_des",
                                    "duration", "mode", "mode_name_fr", "distance", "ghg_emissions_factor",
                                    "cost_factor"])

    persons, travels = standard_emd(pool, persons, travels, "2020")

    conn.close()

    return persons, travels, emd_id, emd_name


def get_emd_by_geo_codes(pool, geo_codes):
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    geo_codes = geo_codes_city_to_district(pool, geo_codes)

    cur.execute("""SELECT COM_AV, COM_AP, DATE_EFF
                   FROM insee_cog_evenements
                   WHERE TYPECOM_AP = "COM" AND YEAR(DATE_EFF) < ? AND YEAR(DATE_EFF) > ?""", ["2020", "2012"]) # 2020 - 2012 good pour lyon
    result = list(cur)
    cog_changes = pd.DataFrame(result, columns=["geo_code_av", "geo_code_ap", "date"])
    cog_changes.sort_values(by="date", ascending=False, inplace=True)

    geo_codes = pd.DataFrame({"geo_code": geo_codes})
    geo_codes = pd.merge(geo_codes, cog_changes, left_on="geo_code", right_on="geo_code_ap", how="left")
    mask_no_changes = geo_codes["geo_code_av"].isna()
    geo_codes.loc[mask_no_changes, "geo_code_av"] = geo_codes.loc[mask_no_changes, "geo_code"]
    geo_codes = geo_codes["geo_code_av"].to_list()

    cur.execute("""SELECT 
                   emd_persons.emd_id, emd_datasets.emd_name, emd_datasets.emd_year
                   FROM emd_persons
                   LEFT JOIN emd_geo ON emd_persons.ra_id = emd_geo.id AND emd_persons.emd_id = emd_geo.emd_id 
                   LEFT JOIN emd_datasets ON emd_persons.emd_id = emd_datasets.emd_id
                   WHERE emd_geo.geo_code IN (""" + ",".join(["?" for g in geo_codes]) + ")", geo_codes)
    result = list(cur)
    emd_ids = pd.DataFrame(result, columns=["emd_id", "emd_name", "emd_year"])
    emd_id = emd_ids["emd_id"].iloc[0]
    emd_name = emd_ids["emd_name"].iloc[0]
    emd_year = emd_ids["emd_year"].iloc[0]

    cur.execute("""SELECT 
                   id_ind, id_hh, w_ind, ra_id, emd_geo.geo_code, sexe, age, status, csp, nb_car, day
                   FROM emd_persons
                   LEFT JOIN emd_geo ON emd_persons.ra_id = emd_geo.id AND emd_persons.emd_id = emd_geo.emd_id 
                   WHERE emd_geo.geo_code IN (""" + ",".join(["?" for g in geo_codes]) + ")", geo_codes)
    result = list(cur)
    persons = pd.DataFrame(result, columns=["id_ind", "id_hh", "w_ind", "ra_id", "geo_code", "sexe", "age", "status",
                                            "csp", "nb_car", "day"])

    cur.execute("""SELECT 
                   emd_persons.id_ind, t.id_trav, t.trav_nb, t.reason_ori,  reasons_ori.name, reasons_ori.name_fr, t.zone_ori, emd_geo_ori.geo_code, t.hour_ori, 
                   t.reason_des, reasons_des.name, reasons_des.name_fr, t.zone_des, emd_geo_des.geo_code, t.hour_des, t.duration, t.modp, modes.name_fr, t.distance,
                   modes_detailed.ghg_emissions_factor, modes_detailed.cost_factor
                   FROM emd_persons
                   LEFT JOIN emd_geo ON emd_persons.ra_id = emd_geo.id AND emd_persons.emd_id = emd_geo.emd_id
                   JOIN emd_travels AS t ON emd_persons.id_ind = t.id_ind
                   JOIN emd_modes_dict ON t.modp = emd_modes_dict.value AND t.emd_id = emd_modes_dict.emd_id
                   JOIN modes_detailed ON emd_modes_dict.mode_id = modes_detailed.id
                   JOIN modes ON modes_detailed.id_main_mode = modes.id
                   JOIN emd_reasons_dict AS reasons_dict_ori ON t.reason_ori = reasons_dict_ori.value AND t.emd_id = reasons_dict_ori.emd_id
                   JOIN emd_reasons AS emd_reasons_ori ON reasons_dict_ori.reason_id = emd_reasons_ori.id
                   JOIN reasons AS reasons_ori ON emd_reasons_ori.id_main_reason = reasons_ori.id
                   JOIN emd_reasons_dict AS reasons_dict_des ON t.reason_des = reasons_dict_des.value AND t.emd_id = reasons_dict_des.emd_id
                   JOIN emd_reasons AS emd_reasons_des ON reasons_dict_des.reason_id = emd_reasons_des.id
                   JOIN reasons AS reasons_des ON emd_reasons_des.id_main_reason = reasons_des.id 
                   LEFT JOIN emd_geo AS emd_geo_ori ON t.zone_ori = emd_geo_ori.id AND t.emd_id = emd_geo_ori.emd_id
                   LEFT JOIN emd_geo AS emd_geo_des ON t.zone_des = emd_geo_des.id AND t.emd_id = emd_geo_des.emd_id
                   WHERE emd_geo.geo_code IN (""" + ",".join(["?" for g in geo_codes]) + ")", geo_codes)
    result = list(cur)
    travels = pd.DataFrame(result, columns=["id_ind", "id_trav", "trav_nb", "reason_ori", "reason_ori_name",
                                            "reason_ori_name_fr", "id_ori", "c_geo_code_ori", "hour_ori",
                                            "reason_des", "reason_des_name", "reason_des_name_fr", "id_des",
                                            "c_geo_code_des", "hour_des", "duration", "mode", "mode_name_fr",
                                            "distance", "ghg_emissions_factor", "cost_factor"])

    persons, travels = standard_emd(pool, persons, travels, "2020")

    conn.close()

    return persons, travels, emd_id, emd_name


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    pool = mariadb_connection_pool()

    montpellier_metropole = ["34022", "34027", "34057", "34058", "34077", "34087", "34088", "34090",
                             "34095", "34116", "34120", "34123", "34129", "34134", "34164", "34169",
                             "34172", "34179", "34198", "34202", "34217", "34227", "34244", "34249",
                             "34256", "34259", "34270", "34295", "34307", "34327", "34337"]

    persons, travels, emd_id, emd_name = get_emd_by_geo_codes(pool, montpellier_metropole)

    print(persons)
    print(travels)

    mask_emp = persons["status"] == "employed"

    print("-- TRAVELS EMPLOYED")
    analysis(persons[mask_emp], travels, "test", False, False)
    print("-- TRAVELS NOT EMPLOYED")
    analysis(persons[~mask_emp], travels, "test", False, False)
    print("-- TRAVELS ALL")
    analysis(persons, travels, "test", False, True)
