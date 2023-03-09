from data_manager.dictionnary.modes import get_modes_entd
from data_manager.dictionnary.reasons import get_reasons_entd

import pandas as pd

from model.commune import ResidentialCommune


def standard_travels(pool, travels):
    modes_entd = get_modes_entd(pool)
    def standard_mode(m):
        return modes_entd.loc[m, "name"]
    def standard_mode_fr(m):
        return modes_entd.loc[m, "name_fr"]
    def standard_ghg_emissions(m):
        return modes_entd.loc[m, "ghg_emissions_factor"]
    def standard_cost(m):
        return modes_entd.loc[m, "cost_factor"]

    reasons_entd = get_reasons_entd(pool)
    def standard_reason(r):
        return reasons_entd.loc[r, "name"]
    def standard_reason_fr(r):
        return reasons_entd.loc[r, "name_fr"]
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
        elif (ori == "domicile" and des == "affaires personnelles") or (des == "domicile" and ori == "affaires personnelles"):
            return "domicile ↔ affaires personnelles"
        else:
            return "autre"

    travels["mode_name"] = travels["mode"].apply(lambda m: standard_mode(m))
    travels["mode_name_fr"] = travels["mode"].apply(lambda m: standard_mode_fr(m))
    travels["ghg_emissions_factor"] = travels["mode"].apply(lambda m: standard_ghg_emissions(m))
    travels["cost_factor"] = travels["mode"].apply(lambda m: standard_cost(m))

    #travels["reason_fr"] = travels["reason_des"].apply(lambda r: standard_reason_fr(r))

    travels["reason_ori_name"] = travels["reason_ori"].apply(lambda r: standard_reason(r))
    travels["reason_des_name"] = travels["reason_des"].apply(lambda r: standard_reason(r))
    travels["reason_ori_name_fr"] = travels["reason_ori"].apply(lambda r: standard_reason_fr(r))
    travels["reason_des_name_fr"] = travels["reason_des"].apply(lambda r: standard_reason_fr(r))

    travels["reason_name_fr"] = travels[["reason_ori_name_fr", "reason_des_name_fr"]].apply(
        lambda r: group_reason_fr(r), axis=1)

    travels["nb_tot_passengers"] = travels["nb_passengers"] + 1

    #sum_w_ind = travels.drop_duplicates(subset=["id"])["w_entd_ind"].sum()
    #travels["w_trav"] = travels["w_entd_trav"] / sum_w_ind
    travels["number"] = 1
    return travels


def compute_attributes(travels, territory):
    def compute_ori_des_geocode(area_id):
        if not pd.isna(area_id):
            commune = territory.get_commune_by_area_id(area_id)
            if hasattr(commune, "zone"):
                return commune.geo_code
            else:
                return commune.geo_code
        else:
            return None

    travels["c_geo_code_ori"] = travels["id_ori"].map(compute_ori_des_geocode)
    travels["c_geo_code_des"] = travels["id_des"].map(compute_ori_des_geocode)

    """
    travels["c_geo_code_ori"] = [territory.get_commune_by_area_id(area_id).geo_code if not pd.isna(area_id) else None
                           for area_id in travels["id_ori"]]
    travels["c_geo_code_des"] = [territory.get_commune_by_area_id(area_id).geo_code if not pd.isna(area_id) else None
                           for area_id in travels["id_des"]]

    travels["zone_ori"] = [territory.get_commune_by_area_id(area_id).zone if hasattr(territory.get_commune_by_area_id(area_id), "zone")
                           else "external"
                           for area_id in travels["c_geo_code_ori"]]
    travels["zone_des"] = ["internal" if isinstance(territory.get_commune_by_area_id(area_id), ResidentialCommune)
                           else "external"
                           for area_id in travels["id_des"]]"""
    return travels


def compute_indicators(travels, distance_matrix):
    #travels["ghg_emissions"] = travels["distance"] * travels["ghg_emissions_factor"] # / travels["nb_tot_passengers"] because emission factor for car is pondered by global car occupancy
    #travels["cost"] = travels["distance"] * travels["cost_factor"] / travels["nb_tot_passengers"]

    #travels["reason"] = travels["reason_des"]
    #home_mask = travels['reason'] == "home"
    #travels.loc[home_mask, 'reason'] = travels.loc[home_mask, 'reason_ori']

    travels["distance_t"] = travels[["id_ori", "id_des"]].apply(
        lambda row: distance_matrix.loc[row["id_ori"], row["id_des"]] if row.notna().all() else None, axis=1)

    mask_dist_none = travels["distance_t"].isna()
    #print(mask_dist_none.sum())
    travels.loc[mask_dist_none, "distance_t"] = travels.loc[mask_dist_none, "distance"]
    travels["distance_emp"] = travels["distance"]
    travels["distance"] = travels["distance_t"]
    travels["ghg_emissions"] = travels["distance"] * travels["ghg_emissions_factor"] / 1000 #tC02eq
    return travels


def compute_zones(travels, territory):
    def compute_ori_des_zone(geo_code):
        if not pd.isna(geo_code):
            commune = territory.get_commune_by_geo_code(geo_code)
            if hasattr(commune, "zone"):
                return commune.zone
            else:
                return -1
        else:
            return None

    travels["zone_ori"] = travels["c_geo_code_ori"].map(compute_ori_des_zone)
    travels["zone_des"] = travels["c_geo_code_des"].map(compute_ori_des_zone)

    return travels

