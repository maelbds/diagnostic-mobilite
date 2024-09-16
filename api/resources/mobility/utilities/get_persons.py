import pandas as pd

from compute_model.database_connection.db_request import db_request


def get_persons(geo_codes):
    result = db_request(
        """ SELECT cp.id_ind, ep.MDATE_jour, 
                   ep.SEXE, ep.AGE, ep.__csp, ep.__status,
                   ep.NPERS, ep.NENFANTS, ep.JNBVEH,
                   ep.STATUTCOM_UU_RES, ep.TAA2017_RES, ep.DENSITECOM_RES,
                   ep.__immo_lun, ep.__immo_mar, ep.__immo_mer,  ep.__immo_jeu,  ep.__immo_ven

            FROM computed_persons AS cp
            JOIN emp_persons AS ep ON cp.id_ind_emp = ep.ident_ind

            WHERE geo_code IN :geo_codes
            """,
        {
            "geo_codes": geo_codes
        })

    persons = pd.DataFrame(result, columns=["id_ind", "jour",
                                            "sexe", "age", "csp", "status",
                                            "nb_pers", "nb_child", "nb_car",
                                            "commune_uu_status", "t_aa", "commune_density",
                                            "immo_lun", "immo_mar", "immo_mer", "immo_jeu", "immo_ven"])
    persons["w_ind"] = 1
    persons = persons.astype({"w_ind": "float64",
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
                              "nb_car": "int32"})

    # ----- STATUS
    persons["status"] = persons["status"].replace("other_18", "other")

    # ----- CSP
    persons.loc[persons["status"] == "retired", "csp"] = 7

    return persons


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    print(get_persons(["79048", "79191"]))

