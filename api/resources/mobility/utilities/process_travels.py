

def process_reason(travels):
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

    travels.loc[:, "reason_name_fr"] = travels.loc[:, ["reason_ori_name_fr", "reason_des_name_fr"]].apply(
        lambda r: group_reason_fr(r), axis=1, result_type="reduce")

    return travels


def process_specific_emd(travels):
    travels["day"] = travels["day"].replace({
        1: "lundi",
        2: "mardi",
        3: "mercredi",
        4: "jeudi",
        5: "vendredi",
    })
    return travels


def process_specific_model(travels):
    travels["w_ind"] = 1

    """travels["nb_passengers"] = travels["passengers_hh"] + travels["passengers_out_hh"]
    travels.drop(columns=["passengers_hh", "passengers_out_hh"], inplace=True)
    travels["nb_tot_passengers"] = travels["nb_passengers"] + 1"""

    return travels