import pandas as pd


def format_syn_pop(syn_pop):
    # create proper id_hh
    syn_pop["new_id_census_hh"] = syn_pop["id_census_hh"]
    mask_duplicates = syn_pop.duplicated()
    i = 1
    while sum(mask_duplicates) > 0:
        syn_pop.loc[mask_duplicates, "new_id_census_hh"] = syn_pop.loc[mask_duplicates, "id_census_hh"] + f"_{i}"
        i += 1
        mask_duplicates = syn_pop.duplicated()
    syn_pop["id_hh"] = syn_pop["geo_code"] + "_" + syn_pop["new_id_census_hh"]

    # create proper id_ind
    syn_pop["id_ind"] = syn_pop["geo_code"] + "_" + syn_pop.index.astype(str)

    syn_pop = syn_pop.loc[:, ["id_ind", "id_hh", "geo_code", "sexe", "age", "status", "csp",
                              "nb_pers", "nb_child", "hh_type", "nb_car",
                              "work_transport", "work_within_commune",
                              "commune_uu_status", "commune_density", "id_census_ind"]]
    syn_pop = syn_pop.astype({"sexe": "int32",
                              "age": "int32",
                              "csp": "int32",
                              "nb_pers": "int32",
                              "nb_child": "int32",
                              "nb_car": "int32",
                              "hh_type": "int32",
                              "work_within_commune": "int32"})

    return syn_pop
