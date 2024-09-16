import pandas as pd
import numpy as np
import os


def read_emd_dataset(emd_id):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    def read_csv(file_name, cols_name):
        data = pd.read_csv(file_name, sep=";", dtype=str, usecols=cols_name)
        return data

    def calc_scholars_status(status, age):
        if status == "scholars":
            if 2 <= age <= 5:
                return "scholars_2_5"
            elif 6 <= age <= 10:
                return "scholars_6_10"
            elif 11 <= age <= 14:
                return "scholars_11_14"
            elif 15 <= age <= 17:
                return "scholars_15_17"
            elif 18 <= age:
                return "scholars_18"
            else:
                return "other"
        else:
            return status

    def read_dataset(dataset_name):
        dic_dataset_name = dictionnary["file"] == dataset_name
        dataset_cols = dictionnary.loc[dic_dataset_name, "emd_variable"].drop_duplicates()
        return read_csv(f"data/{emd_id}/datasets/{dataset_name}.csv", dataset_cols)

    def read_dictionnary_modes(emd_id):
        dict_cols = ["value", "description", "mode_id"]
        return read_csv(f"data/{emd_id}/dictionnary_modes.csv", dict_cols)

    def read_dictionnary_reasons(emd_id):
        dict_cols = ["value", "description", "reason_id"]
        return read_csv(f"data/{emd_id}/dictionnary_reasons.csv", dict_cols)

    def normalize_variables(dataset, dataset_name):
        dic_dataset_name = dictionnary["file"] == dataset_name
        dataset_variables = dictionnary[dic_dataset_name][["emd_variable", "emd_values",
                                                    "diag_mob_variable", "diag_mob_values", "diag_mob_format"]]
        dataset_variables = dataset_variables.groupby("emd_variable").apply(
            lambda df: df[["emd_values", "diag_mob_values"]].set_index("emd_values").to_dict()["diag_mob_values"])
        dataset_variables = dataset_variables.to_dict()
        return dataset.replace(dataset_variables)

    def set_names(dataset, dataset_name):
        dic_dataset_name = dictionnary["file"] == dataset_name
        dataset_col_names = dictionnary[dic_dataset_name][["emd_variable", "diag_mob_variable"]]. \
            drop_duplicates().set_index("emd_variable").to_dict()["diag_mob_variable"]
        return dataset.rename(columns=dataset_col_names)

    def set_types(dataset, dataset_name):
        dic_dataset_name = dictionnary["file"] == dataset_name
        dataset_type = dictionnary[dic_dataset_name][["diag_mob_variable", "diag_mob_format"]]. \
            drop_duplicates().set_index("diag_mob_variable").to_dict()["diag_mob_format"]
        return dataset.astype(dataset_type)

    def get_id(dataset_name, dataset_id):
        id_dict = dictionnary[dictionnary["file"] == dataset_name+"_"+dataset_id]
        dataset_ids = read_csv(f"data/{emd_id}/datasets/{dataset_name}.csv", id_dict["emd_variable"])
        dataset_ids = dataset_ids.astype(
            id_dict[["emd_variable", "diag_mob_format"]].set_index("emd_variable").to_dict()["diag_mob_format"])
        dataset_ids = dataset_ids.astype("string")
        return dataset_ids.agg("-".join, axis=1)

    def check_modes(modes_dict, travels):
        modes_values = modes_dict["value"].to_list()
        travels_modes_p = travels["modp"].drop_duplicates().to_list()
        travels_modes_i = travels["moip"].drop_duplicates().to_list()
        is_modes_p_in_values = all([t_m in modes_values for t_m in travels_modes_p])
        is_modes_i_in_values = all([t_m in modes_values for t_m in travels_modes_i])
        return is_modes_p_in_values & is_modes_i_in_values

    def check_reasons(reasons_dict, travels):
        reasons_values = reasons_dict["value"].to_list()
        travels_reason_ori = travels["reason_ori"].drop_duplicates().to_list()
        travels_reason_des = travels["reason_des"].drop_duplicates().to_list()
        is_reason_ori_in_values = all([t_m in reasons_values for t_m in travels_reason_ori])
        is_reason_des_in_values = all([t_m in reasons_values for t_m in travels_reason_des])
        return is_reason_ori_in_values & is_reason_des_in_values

    print(f"---- {emd_id}")
    dictionnary = pd.read_csv(f"data/{emd_id}/dictionnary.csv", sep=";", dtype=str)

    print("------- PERSONS -------------")
    persons = read_dataset("persons")
    print(persons)
    persons = normalize_variables(persons, "persons")
    persons = set_names(persons, "persons")
    # fix missing values
    persons["status"] = persons["status"].fillna("other")
    persons["csp"] = persons["csp"].fillna("8").replace({"0": "8"})
    persons = persons.replace({"w_ind": {"0": np.nan}}).dropna(subset=["w_ind"])

    persons = set_types(persons, "persons")
    # complete scholars status (need integer age)
    persons["status"] = persons[["status", "age"]].apply(lambda x: calc_scholars_status(x["status"], x["age"]), axis=1)

    # manage ra_id (tira + zf)
    if "ra_id" not in list(persons.columns):
        persons["ra_id"] = persons["tira"] + persons["zf"]
        persons = persons.drop(columns=["tira", "zf"])
    persons["id_ind"] = get_id("persons", "id_ind")
    persons["id_hh"] = get_id("persons", "id_hh")
    print(persons.sort_values(by=["ra_id", "ech", "per"]))

    print("-- quality check")
    persons_only_len = len(persons.index)
    print(persons["status"].drop_duplicates())
    print(persons["csp"].drop_duplicates())
    print(persons["sexe"].drop_duplicates())

    print("------- HOUSEHOLDS -------------")
    households = read_dataset("households")
    households = normalize_variables(households, "households")
    households = set_names(households, "households")
    households = set_types(households, "households")
    households["id_hh"] = get_id("households", "id_hh")
    # manage ra_id (tira + zf)
    if "ra_id" not in list(households.columns):
        households["ra_id"] = households["tira"] + households["zf"]
        households = households.drop(columns=["tira", "zf"])
    print(households.sort_values(by=["ra_id", "ech"]))

    print("------- PERSONS with HOUSEHOLDS -------------")
    persons = pd.merge(persons, households[["id_hh", "nb_car", "w_hh"]], on=["id_hh"], how="left")
    print(persons.sort_values(by=["ra_id", "ech", "per"]))

    print("------- TRAVELS -------------")
    travels = read_dataset("travels")
    travels = normalize_variables(travels, "travels")
    travels = set_names(travels, "travels")
    travels = set_types(travels, "travels")
    travels["id_ind"] = get_id("travels", "id_ind")
    travels["id_trav"] = get_id("travels", "id_trav")
    # manage ra_id (tira + zf)
    if "ra_id" not in list(travels.columns):
        travels["ra_id"] = travels["tira"] + travels["zf"]
        travels = travels.drop(columns=["tira", "zf"])
    # manage time
    if "hour_ori_h" in list(travels.columns):
        travels["hour_ori"] = (travels["hour_ori_h"].astype("int")*100 + travels["hour_ori_m"].astype("int")).astype("str")
        travels["hour_des"] = (travels["hour_des_h"].astype("int")*100 + travels["hour_des_m"].astype("int")).astype("str")
        travels = travels.drop(columns=["hour_ori_h", "hour_ori_m", "hour_des_h", "hour_des_m"])
    travels["distance"] = travels["distance"] / 1000  # kilometers
    print(travels.sort_values(by=["ra_id", "ech", "per"]))

    print("------- Quality check")
    modes_dict = read_dictionnary_modes(emd_id)
    reasons_dict = read_dictionnary_reasons(emd_id)
    print(f"Tous les modes sont dans le dictionnaire : {check_modes(modes_dict, travels)}")
    print(f"Tous les motifs sont dans le dictionnaire : {check_reasons(reasons_dict, travels)}")
    print(f"persons length is kept : {len(persons.index) == persons_only_len}")

    # ADD EMD_ID
    persons["emd_id"] = emd_id
    travels["emd_id"] = emd_id
    modes_dict["emd_id"] = emd_id
    reasons_dict["emd_id"] = emd_id

    print(travels[travels["modp"] != "01"])


    print("------ TRAVELS PARTS")
    """
    travels_parts = read_dataset("travels_parts")
    travels_parts = normalize_variables(travels_parts, "travels_parts")
    travels_parts = set_names(travels_parts, "travels_parts")
    travels_parts = set_types(travels_parts, "travels_parts")
    if "ra_id" not in list(travels_parts.columns):
        travels_parts["ra_id"] = travels_parts["tira"] + travels_parts["zf"]
        travels_parts = travels_parts.drop(columns=["tira", "zf"])
    print(travels_parts.sort_values(by=["ra_id", "ech", "per", "trav_nb", "part_id"]))

    travels_parts["part_nb_passengers"] = travels_parts["part_nb_passengers"].fillna(0)
    travels_parts_modes = travels_parts.groupby(
        ["ra_id", "ech", "per", "trav_nb"], as_index=False)["part_mode"].agg("-".join)
    print(travels_parts_modes)
    travels_parts_passengers = travels_parts.groupby(
        ["ra_id", "ech", "per", "trav_nb"], as_index=False)["part_nb_passengers"].mean().round()
    print(travels_parts_passengers)

    travels = pd.merge(travels, travels_parts_modes, on=["ra_id", "ech", "per", "trav_nb"], how="left")
    travels = pd.merge(travels, travels_parts_passengers, on=["ra_id", "ech", "per", "trav_nb"], how="left")

    missing_values = travels["part_nb_passengers"].isna()
    travels.loc[missing_values, "part_mode"] = travels.loc[missing_values, "modp"]
    print(travels.sort_values(by=["ra_id", "ech", "per"]).head(40))
    """

    #analysis(persons, travels)

    # specific to marseille
    """
    travels["zone_ori"] = travels["zone_ori"].apply(lambda z: z[:6])
    travels["zone_des"] = travels["zone_des"].apply(lambda z: z[:6])
    travels["ra_id"] = travels["ra_id"].apply(lambda z: z[:6])
    persons["ra_id"] = persons["ra_id"].apply(lambda z: z[:6])
    """
    persons = persons.drop(columns=["w_hh", "w_ind_coe1"])

    return persons, travels, modes_dict, reasons_dict


if __name__ == "__main__":
    pd.set_option('display.max_columns', 65)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    emd_id = "montpellier"
    emd_name = "Enquête Déplacements Grand Territoire (EDGT) de l’Aire Métropolitaine de Montpellier (2013-2014)"

    emd_dataset = read_emd_dataset(emd_id)

