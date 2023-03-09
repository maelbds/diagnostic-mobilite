import numpy as np
import pandas as pd

from data_manager.entd_emd.standardisation import adapt_work_distance
from model.territorial_anchorage.uo_model import general_uo_model


def dist_cat(dist):
    categories = [0.5, 1, 5, 10, 15, 20, 30, 50]
    dist_cat = sum([1 for c in categories if dist > c])
    return dist


def set_main_activities(synthetic_population, areas, distances_areas, commuter_matrix,
                        commuter_distances_matrix, set_work_area):
    """

    :param synthetic_population: with residential area id
    :param distances_areas: distances matrix between all areas
    :return: synthetic population with id and dist of main activities : work, education, shopping, services, leisure
    """
    residential_areas = [a for a in areas if a.category == "residential"]
    shopping_areas = [a for a in areas if a.category == "shop_food" or a.category == "shop_goods"]
    services_areas = [a for a in areas if a.category == "services" or
                      a.category == "administrative" or
                      a.category == "medical_common" or
                      a.category == "medical_exceptionnal"]
    leisure_areas = [a for a in areas if a.category == "leisure_outing" or
                     a.category == "leisure_food" or
                     a.category == "activities"]
    work_areas = [a for a in areas if a.category == "work"]

    # --- SHOPPING, LEISURE, SERVICES
    uo_prob_matrix_shopping = general_uo_model(residential_areas, shopping_areas, distances_areas, 0.6, 0)
    shopping_ids = uo_prob_matrix_shopping.columns.tolist()

    uo_prob_matrix_leisure = general_uo_model(residential_areas, leisure_areas, distances_areas, 0.5, 0) # un peu plus homogène
    leisure_ids = uo_prob_matrix_leisure.columns.tolist()

    uo_prob_matrix_services = general_uo_model(residential_areas, services_areas, distances_areas, 0.9, 0) #good
    services_ids = uo_prob_matrix_services.columns.tolist()

    def set_common_activities(row):
        ori_id = row["ra_id"]
        probs_shopping = uo_prob_matrix_shopping.loc[ori_id].to_list()
        shopping_id = np.random.choice(shopping_ids, p=probs_shopping)
        shopping_dist = dist_cat(distances_areas.loc[ori_id, shopping_id])

        probs_leisure = uo_prob_matrix_leisure.loc[ori_id].to_list()
        leisure_id = np.random.choice(leisure_ids, p=probs_leisure)
        leisure_dist = dist_cat(distances_areas.loc[ori_id, leisure_id])

        probs_services = uo_prob_matrix_services.loc[ori_id].to_list()
        services_id = np.random.choice(services_ids, p=probs_services)
        services_dist = dist_cat(distances_areas.loc[ori_id, services_id])
        return [shopping_id, shopping_dist,
                leisure_id, leisure_dist,
                services_id, services_dist]

    common_activities = synthetic_population.apply(
        lambda x: set_common_activities(x), axis=1, result_type='expand').rename(
        columns={0: "shopping_id", 1: "shopping_dist",
                 2: "leisure_id", 3: "leisure_dist",
                 4: "services_id", 5: "services_dist"})

    # --- EDUCATION
    all_education_areas = [a for a in areas if a.category == "education"]

    scholars_2_5 = synthetic_population[(synthetic_population["status"] == "scholars_2_5")]
    pre_school_areas = [a for a in all_education_areas if a.contains_type("pre school")]
    scholars_6_10 = synthetic_population[(synthetic_population["status"] == "scholars_6_10")]
    primary_school_areas = [a for a in all_education_areas if a.contains_type("primary school")]
    scholars_11_14 = synthetic_population[(synthetic_population["status"] == "scholars_11_14")]
    secondary_school_areas = [a for a in all_education_areas if a.contains_type("secondary school")]
    scholars_15 = synthetic_population[(synthetic_population["status"] == "scholars_15_17") |
                                          (synthetic_population["status"] == "scholars_18")]
    high_school_areas = [a for a in all_education_areas if a.contains_type("high school")]

    education_categories = [
        #{"scholars": scholars_2_5, "areas": pre_school_areas},
        {"scholars": scholars_6_10, "areas": primary_school_areas},
        {"scholars": scholars_11_14, "areas": secondary_school_areas},
        {"scholars": scholars_15, "areas": high_school_areas}
    ]

    education = []
    for e in education_categories:
        education_areas = e["areas"] if len(e["areas"]) > 0 else all_education_areas
        scholars = e["scholars"]

        uo_prob_matrix_education = general_uo_model(residential_areas, education_areas, distances_areas)
        education_ids = uo_prob_matrix_education.columns.tolist()

        def set_education_uo(row):
            ori_id = row["ra_id"]
            probs_education = uo_prob_matrix_education.loc[ori_id].to_list()
            education_id = np.random.choice(education_ids, p=probs_education)
            education_dist = dist_cat(distances_areas.loc[ori_id, education_id])
            return [education_id, education_dist, row["id"]]

        def set_education_closest(row):
            ori_id = row["ra_id"]
            distances_education_areas = distances_areas.loc[ori_id, education_ids]
            education_id = distances_education_areas.idxmin(axis=1)
            education_dist = distances_education_areas.min()
            return [education_id, education_dist, row["id"]]

        education_cat = scholars.apply(
            lambda x: set_education_closest(x), axis=1, result_type='expand').rename(
            columns={0: "education_id", 1: "education_dist", 2: "id"})

        education.append(education_cat)
    education = pd.concat(education, ignore_index=True)

    # --- WORK
    employed = synthetic_population[(synthetic_population["status"] == "employed")]

    uo_prob_matrix_work = commuter_matrix.apply(lambda row: row/row.sum(), axis=1)
    work_ids = uo_prob_matrix_work.columns.tolist()

    def set_work(row):
        ori_geo_code = row["geo_code"]
        ra_id = row["ra_id"]
        transport_mode = row["work_transport"]
        work_id = set_work_area(ori_geo_code, int(transport_mode))
        if work_id is None:
            probs_work = uo_prob_matrix_work.loc[ori_geo_code].to_list()
            work_id = np.random.choice(work_ids, p=probs_work)
        work_dist = dist_cat(distances_areas.loc[ra_id, work_id])
        #to manage persons working from home
        if int(transport_mode) == 1:
            work_dist = 0
        return [work_id, work_dist, row["id"]]

    """
    uo_prob_matrix_work = commuter_matrix.apply(lambda row: row/row.sum(), axis=1)
    work_ids = uo_prob_matrix_work.columns.tolist()

    def set_work(row):
        ori_geo_code = row["geo_code"]
        probs_work = uo_prob_matrix_work.loc[ori_geo_code].to_list()
        work_id = np.random.choice(work_ids, p=probs_work)
        work_dist = dist_cat(commuter_distances_matrix.loc[ori_geo_code, work_id])
        return [work_id, work_dist, row["id"]]"""

    work = employed.apply(
        lambda x: set_work(x), axis=1, result_type='expand').rename(
        columns={0: "work_id", 1: "work_dist", 2: "id"})
    work["work_dist_adapted"] = work["work_dist"].apply(adapt_work_distance)

    synthetic_population = pd.merge(synthetic_population, common_activities, left_index=True, right_index=True)
    synthetic_population = pd.merge(synthetic_population, education, on="id", how="left")
    synthetic_population = pd.merge(synthetic_population, work, on="id", how="left")

    synthetic_population.fillna(-10, inplace=True)
    return synthetic_population

