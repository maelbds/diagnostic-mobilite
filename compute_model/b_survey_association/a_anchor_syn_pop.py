import pandas as pd
import numpy as np

from compute_model.b_survey_association.d_set_matching_attributes import adapt_work_distance
from compute_model.u_utilities.b_uo_model import general_uo_model


def set_residential_areas(synthetic_population, residential_areas):
    def find_ra_ids_by_commune(ra_com, syn_pop):
        pop = len(syn_pop.index)
        adjusted_ra_com_pop = ra_com["mass"] / ra_com["mass"].sum() * pop
        ra_ids = ra_com.loc[np.repeat(ra_com.index, adjusted_ra_com_pop), "id"].to_list() * 2
        hh_ra = pd.DataFrame({
            "id_hh": syn_pop["id_hh"],
            "ra_id": ra_ids[:pop]}
        ).drop_duplicates(subset=["id_hh"])
        return hh_ra

    ra_ids = []
    for geo_code, group in synthetic_population.groupby("geo_code"):
        mask_ra_com = residential_areas["geo_code"] == geo_code
        ra_ids.append(find_ra_ids_by_commune(residential_areas.loc[mask_ra_com], group))

    ra_ids = pd.concat(ra_ids)
    synthetic_population = pd.merge(synthetic_population, ra_ids, on="id_hh", how="left")

    return synthetic_population


def dist_cat(dist):
    categories = [0.5, 1, 5, 10, 15, 20, 30, 50]
    dist_cat = sum([1 for c in categories if dist > c])
    return dist


def set_characteristic_areas(syn_pop, all_areas, dist_matrix_areas, commuter_matrix):
    # sort areas by category
    mask_residential_areas = all_areas["category"] == "residential"
    residential_areas = all_areas.loc[mask_residential_areas]
    mask_shopping_areas = all_areas["category"].isin(["shop_food", "shop_goods"])
    shopping_areas = all_areas.loc[mask_shopping_areas]
    mask_services_areas = all_areas["category"].isin(["services", "administrative", "medical_common", "medical_exceptionnal"])
    services_areas = all_areas.loc[mask_services_areas]
    mask_leisure_areas = all_areas["category"].isin(["leisure_outing", "leisure_food", "activities"])
    leisure_areas = all_areas.loc[mask_leisure_areas]
    mask_work_areas = all_areas["category"].isin(["work"])
    work_areas = all_areas.loc[mask_work_areas]

    # --- SHOPPING, LEISURE, SERVICES
    uo_prob_matrix_shopping = general_uo_model(residential_areas, shopping_areas, dist_matrix_areas, 0.6, 0)
    shopping_ids = uo_prob_matrix_shopping.columns.tolist()

    uo_prob_matrix_leisure = general_uo_model(residential_areas, leisure_areas, dist_matrix_areas, 0.5, 0)  # un peu plus homogène
    leisure_ids = uo_prob_matrix_leisure.columns.tolist()

    uo_prob_matrix_services = general_uo_model(residential_areas, services_areas, dist_matrix_areas, 0.9, 0)  # good
    services_ids = uo_prob_matrix_services.columns.tolist()

    def set_common_activities(row):
        ori_id = row["ra_id"]
        probs_shopping = uo_prob_matrix_shopping.loc[ori_id].to_list()
        shopping_id = np.random.choice(shopping_ids, p=probs_shopping)
        shopping_dist = dist_cat(dist_matrix_areas.loc[ori_id, shopping_id])

        probs_leisure = uo_prob_matrix_leisure.loc[ori_id].to_list()
        leisure_id = np.random.choice(leisure_ids, p=probs_leisure)
        leisure_dist = dist_cat(dist_matrix_areas.loc[ori_id, leisure_id])

        probs_services = uo_prob_matrix_services.loc[ori_id].to_list()
        services_id = np.random.choice(services_ids, p=probs_services)
        services_dist = dist_cat(dist_matrix_areas.loc[ori_id, services_id])
        return [shopping_id, shopping_dist,
                leisure_id, leisure_dist,
                services_id, services_dist]

    common_activities = syn_pop.apply(
        lambda x: set_common_activities(x), axis=1, result_type='expand').rename(
        columns={0: "shopping_id", 1: "shopping_dist",
                 2: "leisure_id", 3: "leisure_dist",
                 4: "services_id", 5: "services_dist"})


    # --- EDUCATION
    mask_educ_areas = all_areas["category"] == "education"
    all_education_areas = all_areas.loc[mask_educ_areas]

    scholars_2_5 = syn_pop[(syn_pop["status"] == "scholars_2_5")]
    pre_school_areas = all_education_areas.loc[["pre school" in types for types in all_education_areas["types"]]]
    scholars_6_10 = syn_pop[(syn_pop["status"] == "scholars_6_10")]
    primary_school_areas = all_education_areas.loc[["primary school" in types for types in all_education_areas["types"]]]
    scholars_11_14 = syn_pop[(syn_pop["status"] == "scholars_11_14")]
    secondary_school_areas = all_education_areas.loc[["secondary school" in types for types in all_education_areas["types"]]]
    scholars_15 = syn_pop[(syn_pop["status"] == "scholars_15_17") | (syn_pop["status"] == "scholars_18")]
    high_school_areas = all_education_areas.loc[["high school" in types for types in all_education_areas["types"]]]

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

        uo_prob_matrix_education = general_uo_model(residential_areas, education_areas, dist_matrix_areas)
        education_ids = uo_prob_matrix_education.columns.tolist()

        def set_education_uo(row):
            ori_id = row["ra_id"]
            probs_education = uo_prob_matrix_education.loc[ori_id].to_list()
            education_id = np.random.choice(education_ids, p=probs_education)
            education_dist = dist_cat(dist_matrix_areas.loc[ori_id, education_id])
            return [education_id, education_dist, row["id_ind"]]

        def set_education_closest(row):
            ori_id = row["ra_id"]
            distances_education_areas = dist_matrix_areas.loc[ori_id, education_ids]
            education_id = distances_education_areas.idxmin()
            education_dist = distances_education_areas.min()
            return [education_id, education_dist, row["id_ind"]]

        education_cat = scholars.apply(
            lambda x: set_education_closest(x), axis=1, result_type='expand').rename(
            columns={0: "education_id", 1: "education_dist", 2: "id_ind"})

        education.append(education_cat)
    education = pd.concat(education, ignore_index=True)


    # --- WORK
    mask_employed = syn_pop["status"] == "employed"
    employed = syn_pop.loc[mask_employed]

    commuter_matrix_keys = commuter_matrix.index.to_list()
    employed_attr = list(zip(employed["geo_code"], employed["work_within_commune"], employed["work_transport"]))
    mask_employed_with_attr = [emp_a in commuter_matrix_keys for emp_a in employed_attr]

    employed_with_attr = employed[mask_employed_with_attr]
    employed_without_attr = employed[[not k for k in mask_employed_with_attr]]

    work = []

    for label, group in employed_with_attr.groupby(by=["geo_code", "work_within_commune", "work_transport"]):
        pop_group = len(group)
        work_flows_group = commuter_matrix.loc[label].reset_index(drop=True)

        adapted_work_flows = np.ceil(work_flows_group["flow"] / work_flows_group["flow"].sum() * pop_group)
        adapted_index = np.random.choice(np.repeat(work_flows_group.index, adapted_work_flows), size=pop_group)

        group["work_id"] = work_flows_group.loc[adapted_index, "id"].tolist()
        group["work_geo_code"] = work_flows_group.loc[adapted_index, "work_geo_code"].tolist()
        group["work_dist"] = [dist_matrix_areas.loc[ra_id, w_id] for ra_id, w_id in zip(group["ra_id"], group["work_id"])]
        work.append(group[["id_ind", "work_id", "work_dist", "work_geo_code"]])

    # other employed with no attributes in commuter matrix
    without_attr_group = employed_without_attr.copy()
    pop_group = len(without_attr_group)
    work_flows_group = commuter_matrix.reset_index(drop=True)

    without_attr_index = np.random.choice(np.repeat(work_flows_group.index,
                                                    [max(0, f) for f in work_flows_group["flow"]]), size=pop_group)

    without_attr_group["work_id"] = work_flows_group.loc[without_attr_index, "id"].tolist()
    without_attr_group["work_geo_code"] = work_flows_group.loc[without_attr_index, "work_geo_code"].tolist()
    without_attr_group["work_dist"] = [dist_matrix_areas.loc[ra_id, w_id] for ra_id, w_id
                                       in zip(without_attr_group["ra_id"], without_attr_group["work_id"])]
    work.append(without_attr_group[["id_ind", "work_id", "work_dist", "work_geo_code"]])

    # concat all work ids
    work = pd.concat(work)
    work["work_dist_adapted"] = work["work_dist"].apply(adapt_work_distance)

    syn_pop = pd.merge(syn_pop, common_activities, left_index=True, right_index=True)
    syn_pop = pd.merge(syn_pop, education, on="id_ind", how="left")
    syn_pop = pd.merge(syn_pop, work, on="id_ind", how="left")

    # to check work flows repartition
    """syn_pop_by_work_gc = syn_pop.groupby("work_geo_code").count().sort_values(by="id_ind", ascending=False)
    print(syn_pop_by_work_gc["id_ind"]/syn_pop_by_work_gc["id_ind"].sum())
    commuter_matrix_by_gc = commuter_matrix.groupby("work_geo_code").sum().sort_values(by="flow", ascending=False)
    print(commuter_matrix_by_gc["flow"]/commuter_matrix_by_gc["flow"].sum())"""

    syn_pop.fillna(-10, inplace=True)

    return syn_pop

