import pandas as pd


def clean_persons_with_hh(persons_with_hh):
    def dist_str_to_int(dist_str):
        if dist_str == "Moins de 500m":
            return 0
        elif dist_str == "500m à moins de 1km":
            return 500
        elif dist_str == "1 à moins de 2km":
            return 1000
        elif dist_str == "2 à moins de 5km":
            return 2000
        elif dist_str == "5 à moins de 10km":
            return 5000
        elif dist_str == "10km et plus":
            return 10000
        elif dist_str == "10 à moins de 20km":
            return 10000
        elif dist_str == "20km et plus":
            return 20000
        else:
            return dist_str

    persons_with_hh["CS24"].fillna(value="82", inplace=True)  # 82 : Inactifs divers
    persons_with_hh["SITUA"].fillna(value="8", inplace=True)  # 8 : Moins de 18 ans
    persons_with_hh["BTRAVTEL"].fillna(value=0, inplace=True)
    persons_with_hh["BTRAVNBJ"].fillna(value=0, inplace=True)
    persons_with_hh["dist_res_metro"] = persons_with_hh["dist_res_metro"].apply(lambda x: dist_str_to_int(x))
    persons_with_hh["dist_res_tram"] = persons_with_hh["dist_res_tram"].apply(lambda x: dist_str_to_int(x))
    persons_with_hh["dist_res_train"] = persons_with_hh["dist_res_train"].apply(lambda x: dist_str_to_int(x))
    persons_with_hh["dist_res_tgv"] = persons_with_hh["dist_res_tgv"].apply(lambda x: dist_str_to_int(x))

    persons_with_hh["pond_indC"] = persons_with_hh["pond_indC"].astype("float64")
    return persons_with_hh


def clean_travels(travels):
    # MTP with missing values NaN
    travels.iloc[38647]["mtp"] = "1.1"
    travels.iloc[41238]["mtp"] = "3.1"
    # MMOTIFDES wrong values
    travels.iloc[32333]["MMOTIFDES"] = "3.1"
    travels.iloc[32334]["MOTPREC"] = "3.1"
    travels["MACCOMPM"].fillna(value=0, inplace=True)
    travels["MACCOMPHM"].fillna(value=0, inplace=True)
    return travels


def create_csp(persons_with_hh):
    persons_with_hh["__csp"] = persons_with_hh.apply(lambda row: row["CS24"][0], axis=1)
    return persons_with_hh


def create_status(persons_with_hh):
    def create_status(row):
        situa = int(row["SITUA"])
        age = int(row["AGE"])
        etud = int(row["ETUDIE"])
        if situa == 1 or situa == 2:
            return "employed"
        elif situa == 5:
            return "retired"
        elif situa == 4:
            return "unemployed"
        elif situa == 3:
            if 14 == age:
                return "scholars_11_14"
            elif 15 <= age <= 17:
                return "scholars_15_17"
            elif 18 <= age:
                return "scholars_18"
            else:
                return "other"
        elif situa == 8:
            if etud == 1:
                if 2 <= age <= 5:
                    return "scholars_2_5"
                elif 6 <= age <= 10:
                    return "scholars_6_10"
                elif 11 <= age <= 14:
                    return "scholars_11_14"
                elif 15 <= age <= 17:
                    return "scholars_15_17"
                else:
                    return "other"
            else:
                return "other"
        elif situa == 6:
            return "unemployed"
        else:
            return "other"

    persons_with_hh["__status"] = persons_with_hh.apply(lambda row: create_status(row), axis=1)
    return persons_with_hh


def create_day_type(persons_with_hh):
    def day_to_type(day):
        if day in ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]:
            return 1
        elif day == "samedi":
            return 2
        elif day == "dimanche":
            return 3

    persons_with_hh["TYPEJOUR"] = persons_with_hh.apply(lambda row: day_to_type(row["MDATE_jour"]), axis=1)
    return persons_with_hh


def create_dist_pt(persons_with_hh):
    def dist_code_to_value(code):
        if code == "1":
            return 0
        elif code == "2":
            return 300
        elif code == "3":
            return 600
        elif code == "4":
            return 1000

    persons_with_hh["__dist_pt"] = persons_with_hh.apply(lambda row: dist_code_to_value(row["BLOGDIST"]), axis=1)
    return persons_with_hh


def create_immo_days(persons):
    def set_immo_days(row):
        immo_days = row[["IMMODEP_A", "IMMODEP_B", "IMMODEP_C", "IMMODEP_D", "IMMODEP_E", "IMMODEP_F",
                         "IMMODEP_G"]].to_list() * 3
        survey_day = row["MDATE_jour"]
        delai = row["MDATE_delai"]
        if row["MIMMOSEM"] == "1":
            return ["1"] * 7
        if survey_day is None or survey_day != survey_day:
            return [None] * 7

        days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        survey_day_nb = (days.index(survey_day) + int(delai)) % 7
        return list(reversed(immo_days[survey_day_nb: survey_day_nb + 7]))

    persons_immo = persons.apply(
        lambda x: set_immo_days(x), axis=1, result_type='expand').rename(
        columns={0: "__immo_lun", 1: "__immo_mar",
                 2: "__immo_mer", 3: "__immo_jeu",
                 4: "__immo_ven", 5: "__immo_sam",
                 6: "__immo_dim"})
    persons_immo = persons_immo.fillna(2)
    persons = pd.merge(persons, persons_immo, left_index=True, right_index=True)

    print("Taux d'immobilité :")
    print(persons[["pond_indC", "__immo_lun"]].groupby("__immo_lun").sum() / persons["pond_indC"].sum() * 100)
    print(persons[["pond_indC", "__immo_mar"]].groupby("__immo_mar").sum() / persons["pond_indC"].sum() * 100)
    print(persons[["pond_indC", "__immo_mer"]].groupby("__immo_mer").sum() / persons["pond_indC"].sum() * 100)
    print(persons[["pond_indC", "__immo_jeu"]].groupby("__immo_jeu").sum() / persons["pond_indC"].sum() * 100)
    print(persons[["pond_indC", "__immo_ven"]].groupby("__immo_ven").sum() / persons["pond_indC"].sum() * 100)
    print(persons[["pond_indC", "__immo_sam"]].groupby("__immo_sam").sum() / persons["pond_indC"].sum() * 100)
    print(persons[["pond_indC", "__immo_dim"]].groupby("__immo_dim").sum() / persons["pond_indC"].sum() * 100)

    persons = persons.drop(columns=["IMMODEP_A", "IMMODEP_B", "IMMODEP_C", "IMMODEP_D", "IMMODEP_E", "IMMODEP_F", "IMMODEP_G", "MIMMOSEM", "MDATE_delai"])

    return persons

