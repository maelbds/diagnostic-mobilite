import pandas as pd

from api.resources.mobility.utilities.get_travels_situation import get_travels_situation
from api.resources.mobility.utilities.process_travels import process_reason, process_specific_model, process_specific_emd
from compute_model.database_connection.db_request import db_request
from api.resources.common.cog import COG


def get_travels(geo_codes):
    travels_situation = get_travels_situation(geo_codes)

    travels_columns = ["id_trav", "id_ind", "w_trav", "w_ind",
                       "trav_nb",
                       "day",
                       "hour_ori", "hour_des", "duration",
                       "geo_code",
                       "geo_code_ori", "geo_code_des",
                       "reason_ori", "reason_ori_name", "reason_ori_name_fr",
                       "reason_des", "reason_des_name", "reason_des_name_fr",
                       "mode", "mode_name", "mode_name_fr",
                       "distance"]
    travels = pd.DataFrame(data=None, columns=travels_columns)

    if travels_situation == "model":
        result = db_request(
            """ SELECT ct.id_trav, ct.id_ind, ct.w_trav, ct.w_trav,
                        et.num_dep,
                        et.MDATE_jour,
                        et.MORIHDEP, et.MDESHARR,
                        et.DUREE,
                        
                        ct.geo_code,
                        ct.geo_code_ori, ct.geo_code_des,
    
                        et.MOTPREC, reasons_ori.name, reasons_ori.name_fr,
                        et.MMOTIFDES, reasons_des.name, reasons_des.name_fr,
    
                        et.mtp, modes.name,  modes.name_fr, 
    
                        ct.distance
    
                FROM computed_travels AS ct
                JOIN emp_travels AS et ON ct.id_trav_emp = et.IDENT_DEP
                
                JOIN emp_modes ON emp_modes.id_emp = et.mtp
                JOIN modes_detailed ON emp_modes.id_mode_detailed = modes_detailed.id
                JOIN modes ON modes_detailed.id_main_mode = modes.id
    
                JOIN emp_reasons AS reasons_dict_ori ON et.MOTPREC = reasons_dict_ori.id_emp
                JOIN reasons AS reasons_ori ON reasons_dict_ori.id_reason = reasons_ori.id
    
                JOIN emp_reasons AS reasons_dict_des ON et.MMOTIFDES = reasons_dict_des.id_emp
                JOIN reasons AS reasons_des ON reasons_dict_des.id_reason = reasons_des.id
    
                WHERE ct.geo_code IN :geo_codes
                """,
            {
                "geo_codes": geo_codes
            })

        travels = pd.DataFrame(result, columns=travels_columns, dtype=str)

        travels = process_specific_model(travels)

    if travels_situation == "emd":
        result = db_request(
            """SELECT  t.id_trav, t.id_ind, p.w_ind, p.w_ind, 
                       t.trav_nb, 
                       p.day,
                       
                       hour_ori, hour_des, duration,
                       p_res.CODGEO_DES,
                       p_ori.CODGEO_DES, p_des.CODGEO_DES,
                       t.reason_ori, reasons_ori.name, reasons_ori.name_fr, 
                       t.reason_des, reasons_des.name, reasons_des.name_fr, 
                       modp, modes.name, modes.name_fr,
                       distance
                                      
               FROM emd_travels AS t
               
               LEFT JOIN emd_persons AS p ON t.id_ind = p.id_ind AND t.emd_id = p.emd_id
               LEFT JOIN emd_mobloc AS m ON t.id_trav = m.id_trav AND t.emd_id = m.emd_id

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
               LEFT JOIN insee_arrondissements_passage AS arr_ori ON emd_geo_ori.geo_code = arr_ori.geo_code_district
               LEFT JOIN insee_passage_cog AS p_ori ON arr_ori.geo_code_city = p_ori.CODGEO_INI
               
               LEFT JOIN emd_geo AS emd_geo_des ON t.zone_des = emd_geo_des.id AND t.emd_id = emd_geo_des.emd_id
               LEFT JOIN insee_arrondissements_passage AS arr_des ON emd_geo_des.geo_code = arr_des.geo_code_district
               LEFT JOIN insee_passage_cog AS p_des ON arr_des.geo_code_city = p_des.CODGEO_INI
               
               LEFT JOIN emd_geo AS emd_geo_res ON t.ra_id = emd_geo_res.id AND t.emd_id = emd_geo_res.emd_id
               LEFT JOIN insee_arrondissements_passage AS arr_res ON emd_geo_res.geo_code = arr_res.geo_code_district
               LEFT JOIN insee_passage_cog AS p_res ON arr_res.geo_code_city = p_res.CODGEO_INI
               
               WHERE p_res.CODGEO_DES IN :geo_codes
               
               AND p_ori.year_cog = :cog
               AND p_des.year_cog = :cog
               AND p_res.year_cog = :cog
               AND arr_ori.year_cog = :cog
               AND arr_des.year_cog = :cog
               AND arr_res.year_cog = :cog
               
               AND p.age > 5
               AND p.day < 6
               AND m.mobloc = 1
            """,
            {
                "geo_codes": geo_codes,
                "cog": COG
            })

        travels = pd.DataFrame(result, columns=travels_columns)

        travels = process_specific_emd(travels)

    travels = process_reason(travels)
    travels = travels.astype({"w_trav": "float64",
                              "w_ind": "float64",
                              "trav_nb": "int32",
                              "duration": "int32",
                              "distance": "float64"})

    return travels


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    print("ok")

    lyon_metropole = ["69003", "69029", "69033", "69034", "69040", "69044", "69046", "69271", "69063", "69273", "69068", "69069", "69071", "69072", "69275", "69081", "69276", "69085", "69087", "69088", "69089", "69278", "69091", "69096", "69100", "69279", "69142", "69250", "69116", "69117", "69123", "69127", "69282", "69283", "69284", "69143", "69149", "69152", "69153", "69163", "69286", "69168", "69292", "69293", "69296", "69191", "69194", "69199", "69204", "69205", "69207", "69290", "69233", "69202", "69244", "69256", "69259", "69260", "69266"]

    travels = get_travels(lyon_metropole)
    print(travels)
    print(travels.groupby("geo_code").count().head(50))