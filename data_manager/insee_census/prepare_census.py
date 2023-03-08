def filter_cities(census):
    # remove people living in city
    census = census[census["IRIS"] == "ZZZZZZZZZ"]
    return census


def filter_households(census):
    # remove people with no households
    census = census.loc[(census.loc[:, "INPER"] != "Y") &
                        (census.loc[:, "INPER"] != "Z") &
                        (census.loc[:, "NUMMI"] != "Z")]
    return census


def add_proper_household_id(census):
    # case of people not in household
    census = census.astype({"NUMMI": "int64",
                            "CANTVILLE": "int64"})
    census["id_census_hh"] = census["CANTVILLE"] * 1000000 + census["NUMMI"]
    return census


def complete_missing_nenfr(census):
    def find_child_nb(hh_id):
        mask_hh = census["id_census_hh"] == hh_id
        child_nb = census.loc[mask_hh, "NENFR"].mode().iloc[0]
        return child_nb if child_nb != "Z" else 0
    mask_missing_nenfr = census["NENFR"] == "Z"
    census.loc[mask_missing_nenfr, "NENFR"] = census.loc[mask_missing_nenfr, "id_census_hh"].apply(lambda x: find_child_nb(x))
    return census


def create_status_attribute(census):
    def create_status(row):
        tact = int(row["TACT"])
        age = int(row["AGED"])
        etud = int(row["ETUD"])
        if tact == 11:
            return "employed"
        elif tact == 21:
            return "retired"
        elif tact == 12:
            return "unemployed"
        elif tact == 22:
            if 14 == age:
                return "scholars_11_14"
            elif 15 <= age <= 17:
                return "scholars_15_17"
            elif 18 <= age:
                return "scholars_18"
            else:
                return "other"
        elif tact == 23:
            if etud == 1:
                if 2 <= age <= 5:
                    return "scholars_2_5"
                elif 6 <= age <= 10:
                    return "scholars_6_10"
                elif 11 <= age <= 14:
                    return "scholars_11_14"
                else:
                    return "other"
            else:
                return "other"
        elif tact == 24:
            return "unemployed"
        else:
            return "other"

    census["status"] = census.apply(lambda row: create_status(row), axis=1)
    return census


def create_work_within_commune(census):
    workers_in_commune = census["ILT"] == "1"
    census.loc[workers_in_commune, "work_within_commune"] = 1
    census["work_within_commune"].fillna(value=0, inplace=True)
    return census


def create_hh_type(census):
    census["TYPMR"] = census["TYPMR"].astype("float64")
    census["TYPMR"] = census["TYPMR"]/10
    census["TYPMR"] = census["TYPMR"].astype("int32")
    return census


def create_hh_cars_nb(census):
    census.loc[census["VOIT"] == "3", "VOIT"] = "2"  # change "Trois voiture ou plus" to "Deux voitures ou plus"
    return census


def format_names_types(census):
    census = census.rename(columns={
        "ID": "id_census_ind",
        "IPONDI": "w_census_ind",
        "SEXE": "sexe",
        "AGED": "age",
        "CS1": "csp",
        "INPER": "nb_pers",
        "NENFR": "nb_child",
        "TYPMR": "hh_type",
        "VOIT": "nb_car",
        "TRANS": "work_transport"
    })
    census.drop(columns=["NUMMI", "CANTVILLE", "TACT", "ETUD", "ILT"], inplace=True)
    census = census.astype({"w_census_ind": "float64",
                            "id_census_hh": "str",
                            "sexe": "int32",
                            "age": "int32",
                            "csp": "int32",
                            "nb_pers": "int32",
                            "nb_child": "int32",
                            "nb_car": "int32",
                            "work_within_commune": "int32"})
    return census


def prepare_census(census):
    # census = filter_cities(census)
    census = filter_households(census)
    census = add_proper_household_id(census)
    census = complete_missing_nenfr(census)
    census = create_status_attribute(census)
    census = create_work_within_commune(census)
    census = create_hh_type(census)
    census = create_hh_cars_nb(census)
    census = format_names_types(census)
    census.loc[census["status"] == "retired", "csp"] = 7
    return census

