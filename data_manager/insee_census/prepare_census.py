import pandas as pd


def filter_without_households(census, cols):
    # people without households represents 2.2% of total pop
    mask_people_with_household = (census.loc[:, "INPER"] != "Y") & \
                                 (census.loc[:, "INPER"] != "Z") & \
                                 (census.loc[:, "NUMMI"] != "Z")
    census = census.loc[mask_people_with_household].copy(deep=False)
    #cols.update({"with_household": "INT(1)"})
    return census


def add_proper_household_id(census, cols):
    census["id_census_hh"] = census["CANTVILLE"].astype(str) + "_" + census["NUMMI"].astype(str)
    cols.update({"id_census_hh": "VARCHAR(20)"})
    return census


def complete_missing_nenfr(census, cols):
    census_nb_child = census.groupby("id_census_hh", as_index=None)[["NENFR"]].agg(lambda x: x.mode().iloc[0])
    census_nb_child["nb_child"] = census_nb_child["NENFR"].replace({"Z": 0})
    census = pd.merge(census, census_nb_child[["id_census_hh", "nb_child"]], on="id_census_hh", how="left")
    cols.update({"nb_child": "INT(2)"})
    return census


def create_status_attribute(census, cols):
    def create_status(tact, age, etud):
        tact = int(tact)
        age = int(age)
        etud = int(etud)
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

    census["status"] = [create_status(tact, age, etud) for tact, age, etud
                        in zip(census["TACT"], census["AGED"], census["ETUD"])]
    cols.update({"status": "VARCHAR(15)"})
    return census


def create_work_within_commune(census, cols):
    workers_in_commune = census["ILT"] == "1"
    census.loc[workers_in_commune, "work_within_commune"] = 1
    census["work_within_commune"].fillna(value=0, inplace=True)
    cols.update({"work_within_commune": "INT(1)"})
    return census


def create_hh_type(census, cols):
    typmr = census["TYPMR"].astype("float64")
    typmr = typmr/10
    typmr = typmr.astype("int32")
    census["hh_type"] = typmr
    cols.update({"hh_type": "INT(1)"})
    return census


def create_hh_cars_nb(census, cols):
    census["nb_car"] = census["VOIT"]
    census.loc[census["nb_car"] == "3", "nb_car"] = "2"  # change "Trois voiture ou plus" to "Deux voitures ou plus"
    cols.update({"nb_car": "INT(1)"})
    return census


def complete_csp(census, cols):
    census["csp"] = census["CS1"]
    mask_retired = census["status"] == "retired"
    census.loc[mask_retired, "csp"] = 7
    cols.update({"csp": "INT(1)"})
    return census


def prepare_census(census):
    cols = {}
    census = filter_without_households(census, cols)
    census = add_proper_household_id(census, cols)
    census = complete_missing_nenfr(census, cols)
    census = create_status_attribute(census, cols)
    census = create_work_within_commune(census, cols)
    census = create_hh_type(census, cols)
    census = create_hh_cars_nb(census, cols)
    census = complete_csp(census, cols)
    return census, cols

