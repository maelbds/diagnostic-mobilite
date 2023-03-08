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
    print(",".join(geo_codes))
    print(geo_codes)
    print(len(geo_codes))

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
    print(geo_codes)
    print(len(geo_codes))

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
    marseille_bassin = ["13055"]
    marseille_metropole = ['13001', '13002', '13003', '13005', '13007', '13008', '13009', '13012', '13013', '13014', '13015', '13016', '13019', '13020', '13021', '13022', '13023', '13024', '13025', '13026', '13028', '13029', '13030', '13031', '13032', '13033', '13035', '13037', '13039', '13040', '13041', '13042', '13043', '13044', '13046', '13047', '13048', '13049', '13050', '13051', '13053', '13054', '13055', '13056', '13059', '13060', '13062', '13063', '13069', '13070', '13071', '13072', '13073', '13074', '13075', '13077', '13078', '13079', '13080', '13081', '13082', '13084', '13085', '13086', '13087', '13088', '13090', '13091', '13092', '13093', '13095', '13098', '13099', '13101', '13102', '13103', '13104', '13105', '13106', '13107', '13109', '13110', '13111', '13112', '13113', '13114', '13115', '13117', '13118', '13119', '83120', '84089']

    aubagne_bassin = ["13028", "13022", "13023", "13085", "13119", "13070",
               "13005", "13042", "13030", "13086", "13007", "83120",
               "13016", "13031", "13073", "13013", "13101", "13020"]

    cc_sud_luberon = ['84147', '84133', '84113', '84084', '84076', '84026', '84024', '84014', '84010', '84002', '84151', '84121', '84090', '84052', '84042', '84009']
    ca_terres_de_provence = ['13076', '13116', '13083', '13066', '13052', '13045', '13036', '13027', '13018', '13010', '13089', '13067', '13064']

    cc_val_dauphine = ['38509', '38377', '38315', '38001', '38398', '38381', '38343', '38076', '38401', '38341', '38064', '38560', '38520', '38508', '38464', '38434', '38420', '38369', '38357', '38354', '38323', '38296', '38257', '38246', '38183', '38162', '38148', '38147', '38104', '38098', '38089', '38047', '38044', '38038', '38029', '38012']
    cc_beaujolais_pierre_doree = ['69246', '69245', '69239', '69230', '69212', '69159', '69156', '69140', '69134', '69126', '69125', '69122', '69121', '69113', '69111', '69106', '69090', '69059', '69056', '69055', '69052', '69050', '69049', '69047', '69039', '69026', '69024', '69020', '69017', '69009', '69005', '69004']
    cc_balcon_dauphine = ['38261', '38465', '38050', '38554', '38542', '38539', '38535', '38532', '38515', '38507', '38488', '38467', '38451', '38415', '38392', '38374', '38294', '38282', '38260', '38250', '38210', '38190', '38176', '38146', '38138', '38109', '38067', '38026', '38010', '38546', '38543', '38525', '38494', '38483', '38458', '38365', '38320', '38297', '38295', '38247', '38139', '38135', '38124', '38083', '38055', '38054', '38022']

    cc_lyon_st_exupery = ["38011", "38085", "38097", "38197", "38316", "38507", "38557"]

    #test_marseille_2 = ["13026", "13104", "13021", "13033", "13088", "13043", "13054"]
    marseille_pertuis = ["84089", "13059", "13074", "13048", "13099"]
    marseille_gardanne = ["13015", "13041", "13107"]

    marseille_pertuis_luberon = ['84147', '84133', '84113', '84084', '84076', '84026', '84024', '84014', '84010', '84002', '84151', '84121', '84090', '84052', '84042', '84009', '84089', '84074', '84093', '84065', '84095', '84068', '84140']
    #marseille_pertuis_luberon.remove("84089")
    marseille_baux_provence = ['13076', '13116', '13083', '13066', '13052', '13045', '13036', '13027', '13018', '13010', '13089', '13067', '13064', '13100', '13094', '13057', '13068', '13038', '13065', '13058', '13034', '13011', '13006']


    persons, travels, emd_id, emd_name = get_emd_by_geo_codes(pool, cc_sud_luberon)
    #persons, travels, emd_id, emd_name = get_emd_by_id(pool, "lyon")

    print(persons)
    print(persons["w_ind"].sum())
    print(travels)

    travels_mask_tc = travels["mode_name_fr"] == "transport en commun"
    travels_mask_100km = travels["distance"] < 80

    travels_mask_no_geocode = travels["c_geo_code_ori"].isna() | travels["c_geo_code_des"].isna()
    print(" -- TRAVELS Transport en commun")
    print(travels[travels_mask_tc])
    print(" -- TRAVELS No geocode")
    print(travels[travels_mask_no_geocode])

    mask_emp = persons["status"] == "employed"
    mask_women = persons["sexe"] == 2
    mask_scholar = persons["status"].isin(
        ["scholars_2_5", "scholars_6_10", "scholars_11_14", "scholars_15_17", "scholars_18"])
    mask_scholar_6 = persons["status"] == "scholars_6_10"
    mask_scholar_15 = persons["status"] == "scholars_15_17"

    print("-- focus employed persons")
    print(persons[mask_emp])
    print(persons[mask_emp][["w_ind", "csp"]].groupby("csp").sum())
    print(persons[mask_emp][["w_ind", "nb_car"]].groupby("nb_car").sum()/persons[mask_emp]["w_ind"].sum()*100)
    print(persons[mask_emp][["w_ind", "sexe"]].groupby("sexe").sum()/persons[mask_emp]["w_ind"].sum()*100)

    print("-- TRAVELS EMPLOYED")
    analysis(persons[mask_emp], travels, "test", False, False)
    print("-- TRAVELS NOT EMPLOYED")
    analysis(persons[~mask_emp], travels, "test", False, False)
    print("-- TRAVELS ALL")
    analysis(persons, travels, "test", False, True)

    mask_persons_4travels = persons["id_ind"].isin(travels.loc[travels["trav_nb"]>4, "id_ind"])

    print(persons[mask_emp & mask_persons_4travels])
    total = persons.loc[mask_emp & mask_persons_4travels, "w_ind"].sum()
    total_emp = persons.loc[mask_emp, "w_ind"].sum()
    print(persons[mask_emp & mask_persons_4travels].groupby("csp").sum()/total*100)
    print(persons[mask_emp].groupby("csp").sum()/total_emp*100)
    print(persons[mask_emp & mask_persons_4travels].groupby("sexe").sum()/total*100)
    print(persons[mask_emp].groupby("sexe").sum()/total_emp*100)
    print(persons[mask_emp & mask_persons_4travels].groupby("nb_pers").sum()/total*100)
    print(persons[mask_emp].groupby("nb_pers").sum()/total_emp*100)

    persons.loc[persons["status"] == "retired", "csp"] = 7
    print(persons[persons["csp"].isna()])
    mask_plus15ans = persons["age"] >= 15
    total_pop = persons[mask_plus15ans]["w_ind"].sum()
    print(total_pop)
    print(persons[mask_plus15ans].groupby("csp").sum()/total_pop*100)
    print(persons[mask_plus15ans].groupby("csp").count())
    print(persons[mask_plus15ans].groupby("status").sum()/total_pop*100)
    print(persons[mask_plus15ans].groupby("status").count())

    total_pop = persons["w_ind"].sum()
    print(total_pop)
    print(persons.groupby("status").sum()/total_pop*100)
    print(pd.DataFrame({"pop": persons.groupby("status").sum()["w_ind"].round(),
                        "%": (persons.groupby("status").sum()["w_ind"]/total_pop*100).round(1),
                        "enquete": persons.groupby("status").count()["w_ind"]}))

    mask_travels_travail_autre = travels["reason_name_fr"] == "travail ↔ autre"
    mask_travels_travail_ori = travels["reason_ori_name_fr"] == "travail"
    mask_travels_travail_des = travels["reason_des_name_fr"] == "travail"
    #print(travels[mask_travels_travail_autre])
    #print(travels[mask_travels_travail_autre & mask_travels_travail_ori & mask_travels_travail_des])

    print(travels[(travels["c_geo_code_ori"]=="69123")].groupby("c_geo_code_des").count())
    print(travels[(travels["c_geo_code_des"]=="69123")].groupby("c_geo_code_ori").count())

    print(persons[persons["geo_code"]=="69009"])

    print(persons[persons["status"]=="scholars_18"])

    """persons_with_no_geocode = persons[persons["geo_code"].isna()]
    print(persons_with_no_geocode)
    print(persons_with_no_geocode["w_ind"].sum())
    print(persons_with_no_geocode.groupby("status").sum())
    
    travels_with_no_geocode = travels[travels["c_geo_code_ori"].isna() | travels["c_geo_code_des"].isna()]
    travels_with_geocode = travels_with_no_geocode.merge(persons[["id", "w_ind"]], on="id")
    print(travels_with_no_geocode)
    
    internal_travels = travels[~(travels["c_geo_code_ori"].isna() | travels["c_geo_code_des"].isna())]

    print(travels.dropna(subset=["id_ori", "id_des"]))
    print(travels.drop_duplicates(subset="id").merge(persons, on="id")["w_ind"].sum())

    travels = pd.merge(travels, persons, on="id")

    travels["is_+80"] = travels["distance"] > 80

    travels["number"] = 1
    print(travels)

    travels[["number", "distance"]] = travels[["number", "distance"]].multiply(travels["w_ind"], axis=0)
    print(travels.groupby("is_+80").sum())"""




