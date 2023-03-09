import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError
from data_manager.ign.commune_center import get_coords
from data_manager.insee_general.districts import list_district_to_city


def standard_indicators(travels):
    travels["ghg_emissions"] = travels["distance"] * travels["ghg_emissions_factor"] / 1000  # tC02eq
    travels["cost"] = travels["distance"] * travels["cost_factor"]
    travels["number"] = 1
    return travels


def standard_reason(travels):
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

    travels["reason_name_fr"] = travels[["reason_ori_name_fr", "reason_des_name_fr"]].apply(
        lambda r: group_reason_fr(r), axis=1)

    return travels


def standard_specific_emd(pool, persons, travels, year_cog):
    persons = persons[persons["age"] > 5]
    persons.loc[:, "day_type"] = 1
    persons.loc[:, "day"] = persons.loc[:, "day"].replace({1: "lundi",
                                                           2: "mardi",
                                                           3: "mercredi",
                                                           4: "jeudi",
                                                           5: "vendredi",
                                                           })

    persons_nb_pers = persons[["id_hh", "sexe"]].groupby("id_hh").count().rename(columns={"sexe": "nb_pers"})
    persons = pd.merge(persons, persons_nb_pers, on="id_hh")

    persons["car/pers"] = persons["nb_car"] / persons["nb_pers"]

    persons["w_trav"] = persons["w_ind"]

    travels["distance"] = travels["distance"] / 1000
    travels["distance_t"] = travels["distance"] / 1000

    persons["geo_code"] = list_district_to_city(pool, persons["geo_code"].to_list())
    travels["c_geo_code_ori"] = list_district_to_city(pool, travels["c_geo_code_ori"].to_list())
    travels["c_geo_code_des"] = list_district_to_city(pool, travels["c_geo_code_des"].to_list())

    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT COM_AV, COM_AP, DATE_EFF
                   FROM insee_cog_evenements
                   WHERE TYPECOM_AP = "COM" AND YEAR(DATE_EFF) < ?""", [year_cog])
    result = list(cur)
    conn.close()

    cog_changes = pd.DataFrame(result, columns=["geo_code_av", "geo_code_ap", "date"])
    cog_changes.sort_values(by="date", ascending=False, inplace=True)
    cog_changes.drop_duplicates(subset=["geo_code_av"], inplace=True)
    cog_changes.drop(columns=["date"], inplace=True)

    persons = pd.merge(persons, cog_changes, left_on="geo_code", right_on="geo_code_av", how="left")
    mask_persons_no_cog_changes = persons["geo_code_ap"].isna()
    persons.loc[~mask_persons_no_cog_changes, "geo_code"] = persons.loc[~mask_persons_no_cog_changes, "geo_code_ap"]
    persons.drop(columns=["geo_code_av", "geo_code_ap"], inplace=True)

    travels = pd.merge(travels, cog_changes, left_on="c_geo_code_ori", right_on="geo_code_av", how="left")
    mask_travels_no_cog_changes = travels["geo_code_ap"].isna()
    travels.loc[~mask_travels_no_cog_changes, "c_geo_code_ori"] = travels.loc[
        ~mask_travels_no_cog_changes, "geo_code_ap"]
    travels.drop(columns=["geo_code_av", "geo_code_ap"], inplace=True)

    travels = pd.merge(travels, cog_changes, left_on="c_geo_code_des", right_on="geo_code_av", how="left")
    mask_travels_no_cog_changes = travels["geo_code_ap"].isna()
    travels.loc[~mask_travels_no_cog_changes, "c_geo_code_des"] = travels.loc[
        ~mask_travels_no_cog_changes, "geo_code_ap"]
    travels.drop(columns=["geo_code_av", "geo_code_ap"], inplace=True)

    # to identify travels within 80km from home
    all_geo_codes = pd.concat([persons["geo_code"],
                               travels["c_geo_code_ori"].rename("geo_code"),
                               travels["c_geo_code_des"].rename("geo_code")]).drop_duplicates()

    def get_coords_with_none(geo_code):
        if geo_code is None:
            return None
        else:
            try:
                return get_coords(pool, geo_code)
            except UnknownGeocodeError:
                return None

    all_coords = all_geo_codes.apply(lambda gc: get_coords_with_none(gc))
    coords_by_geo_code = pd.DataFrame({"geo_code": all_geo_codes, "coords": all_coords}).set_index("geo_code")

    def calc_estimated_dist(coord1, coord2):
        if coord1 is None or coord2 is None:
            return None
        X = np.array(coord1)
        Y = np.array(coord2)
        conv_deg_km = np.array([np.pi / 180 * 6400, np.pi / 180 * 4400])
        crow_fly_dist = abs(np.linalg.norm(np.multiply(X - Y, conv_deg_km)))
        return crow_fly_dist

    distances_matrix = pd.DataFrame({
        id_to: coords_by_geo_code.apply(lambda row: calc_estimated_dist(row["coords"], coord_to), axis=1)
        for id_to, coord_to in zip(coords_by_geo_code.index, coords_by_geo_code["coords"])
    })

    travels = pd.merge(travels, persons[["id_ind", "geo_code"]], on="id_ind")
    travels["dist_ori"] = [distances_matrix.loc[ori, des] for ori, des in
                           zip(travels["geo_code"], travels["c_geo_code_ori"])]
    travels["dist_des"] = [distances_matrix.loc[ori, des] for ori, des in
                           zip(travels["geo_code"], travels["c_geo_code_des"])]
    travels["dist_ori"] = travels["dist_ori"].fillna(100)
    travels["dist_des"] = travels["dist_des"].fillna(100)

    travels["mobloc"] = (travels["dist_ori"] < 80) & (travels["dist_des"] < 80)
    travels["mobloc"] = [1 if ml else 0 for ml in travels["mobloc"]]

    travels = travels[travels["mobloc"] == 1]
    return persons, travels


def standard_specific_entd(pool, travels):
    travels["nb_passengers"] = travels["passengers_hh"] + travels["passengers_out_hh"]
    travels.drop(columns=["passengers_hh", "passengers_out_hh"], inplace=True)
    travels["nb_tot_passengers"] = travels["nb_passengers"] + 1

    # out of scolar holidays
    travels = travels.loc[travels["vac_scol"] == 0]
    travels.loc[:, "w_trav"] = travels.loc[:, "w_trav"] * 52 / 36

    # week day only
    travels = travels.loc[travels["day_type"] == 1]
    travels.loc[:, "w_trav"] = travels.loc[:, "w_trav"] / 5
    return travels


def adapt_work_distance(dist):
    return min(dist, 400) ** (1 / 4)
