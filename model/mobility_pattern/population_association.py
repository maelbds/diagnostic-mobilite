import pandas as pd
import numpy as np

from sklearn.preprocessing import OneHotEncoder

from data_manager.entd_emd.analysis import analysis as analysis_emd

from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

attr_cat_emp = {
    "work_transport": 2,
    "sexe": 0.5,
    "commune_uu_status": 1,
    "csp": 1
}

attr_quant_emp = {
    "age": 5,
    "nb_pers": 1,
    "nb_child": 1,
    "work_dist_adapted": 10,
}

attr_cat_not_emp = {
    "status": 2,
    "sexe": 0.5,
    "commune_uu_status": 1,
}

attr_quant_not_emp = {
    "age": 5,
    "nb_pers": 2,
    "nb_child": 2,
    "nb_car": 1.5,
}

matching_tests = []


def comparison(synthetic_population, population_matched):
    print("---- comparison")

    comparison = []
    for attr in ["status", "work_transport", "commune_uu_status", "nb_pers", "nb_child", "nb_car", "csp"]:
        attr_syn_pop = synthetic_population[["id_ind", attr]].groupby(attr).count().rename(
            columns={"id_ind": "synthetic pop"})
        attr_match_pop = population_matched[["id_ind", attr]].groupby(attr).count().rename(
            columns={"id_ind": "matched pop"})
        print(pd.concat([attr_syn_pop, attr_match_pop], axis=1).fillna(0).astype("int"))
        comparison.append(pd.concat([attr_syn_pop, attr_match_pop], axis=1).fillna(0).astype("int"))
    print(pd.concat(comparison))

    syn_pop = synthetic_population[["id_ind", "work_dist", "work_transport"]].copy()
    pop_m = population_matched[["id_ind", "work_dist", "work_transport"]].copy()
    syn_pop["dist_work_cat"] = np.floor(syn_pop["work_dist"] / 10) * 10
    pop_m["dist_work_cat"] = np.floor(pop_m["work_dist"] / 10) * 10

    print("-syn pop")
    print(syn_pop[["id_ind", "dist_work_cat"]].groupby("dist_work_cat").count())
    print("-pop matched")
    print(pop_m[["id_ind", "dist_work_cat"]].groupby("dist_work_cat").count())

    print("-syn pop")
    print(syn_pop[syn_pop["work_transport"] == "6"].groupby("dist_work_cat").count())
    print("-pop matched")
    print(pop_m[pop_m["work_transport"] == "6"].groupby("dist_work_cat").count())

    print(population_matched[population_matched["work_transport"] == "6"]["w_ind"].sum())


def prepare_data_for_nneighbors(synthetic_population, sources,
                                matching_attributes_categorical, matching_attributes_quantitative):
    def std_features(dataset):
        if "nb_pers" in dataset.columns:
            dataset["nb_pers"] = [min(nb, 4) for nb in dataset["nb_pers"]]
        if "nb_child" in dataset.columns:
            dataset["nb_child"] = [min(nb, 2) for nb in dataset["nb_child"]]
        if "work_dist" in dataset.columns:
            dataset["work_dist"] = dataset["work_dist"].fillna(0)
        return dataset

    def weight_attributes(attributes, weights):
        attributes = np.array([[a[i] * w for i, w in enumerate(weights)] for a in attributes])
        return attributes

    matching_attributes_quantitative = {attr: coef for attr, coef in matching_attributes_quantitative.items() if coef>0}
    matching_attributes_categorical = {attr: coef for attr, coef in matching_attributes_categorical.items() if coef > 0}

    min_max_scaler = MinMaxScaler()
    one_hot = OneHotEncoder()

    # print("-- standardize sources = samples")
    sources_quant = sources.loc[:, matching_attributes_quantitative.keys()]  # + ["w_ind"]]
    std_sources_quant = std_features(sources_quant).to_numpy()
    minmax_sources_quant = min_max_scaler.fit_transform(std_sources_quant)

    sources_cat = sources.loc[:,
                  matching_attributes_categorical.keys()]  # list(matching_attributes.keys()) + ["w_ind"]]
    onehot_sources_cat = one_hot.fit_transform(sources_cat.to_numpy()).toarray()

    std_samples = np.concatenate((minmax_sources_quant, onehot_sources_cat), axis=1)

    ponderation_coefs = list(matching_attributes_quantitative.values()) + \
                        sum([[coef] * len(cat) for coef, cat
                             in zip(matching_attributes_categorical.values(), one_hot.categories_)], [])

    std_samples = weight_attributes(std_samples, ponderation_coefs)

    # print("-- standardize synthetic pop")
    syn_pop_quant = synthetic_population.loc[:, matching_attributes_quantitative.keys()]
    # syn_pop_quant["w_ind"] = sources["w_ind"].mean()
    std_syn_pop_quant = std_features(syn_pop_quant).to_numpy()
    minmax_syn_pop_quant = min_max_scaler.transform(std_syn_pop_quant)

    syn_pop_cat = synthetic_population.loc[:,
                  matching_attributes_categorical.keys()]  # list(matching_attributes.keys()) + ["w_ind"]]
    onehot_syn_pop_cat = one_hot.transform(syn_pop_cat.to_numpy()).toarray()

    std_X = np.concatenate((minmax_syn_pop_quant, onehot_syn_pop_cat), axis=1)
    std_X = weight_attributes(std_X, ponderation_coefs)

    return std_X, std_samples, min_max_scaler


def find_nneighbors(std_X, std_samples, nneighbors=20, radius=0.5):
    # print("-- compute nearest neighbors")
    neigh = NearestNeighbors(n_neighbors=nneighbors, radius=radius, metric="manhattan")
    neigh.fit(std_samples)

    #print("-- find nearest neighbors")
    r_neighbors_dist, r_neighbors_index = neigh.radius_neighbors(std_X, return_distance=True)
    n_neighbors_dist, n_neighbors_index = neigh.kneighbors(std_X, return_distance=True)

    neighbors_index = [ri if len(ri) >= nneighbors else ni for ri, ni in zip(r_neighbors_index, n_neighbors_index)]
    return neighbors_index


def nneighbors_index_to_id(n_neighbors_index, sources):
    def indexes_to_ind(indexes):
        weights = sources.iloc[indexes]["w_ind"]
        ind = np.random.choice(indexes, p=weights / weights.sum())
        # indexes = pd.DataFrame({"neighbors_index": indexes})
        # indexes = pd.merge(indexes, sources[["id_ind", "w_ind"]], left_on="neighbors_index", right_index=True, how="left")
        # matched_id = indexes.sample(weights=indexes["w_ind"]).iloc[0]["id_ind"]
        return ind

    matched_indexes = [indexes_to_ind(indexes) for indexes in n_neighbors_index]
    matched_ids = sources.iloc[matched_indexes]["id_ind"]
    # matched_ids = [neigh_to_id(ind) for ind in n_neighbors_index]
    return matched_ids


def standardize_and_match(synthetic_population, sources, matching_attributes_categorical,
                          matching_attributes_quantitative,
                          nneighbors, radius):
    print("- prepare data")
    std_X, std_samples, min_max_scaler = prepare_data_for_nneighbors(synthetic_population, sources,
                                                                     matching_attributes_categorical,
                                                                     matching_attributes_quantitative)

    print("- find nearest neighbors")
    n_neighbors_index = find_nneighbors(std_X, std_samples, nneighbors, radius)
    matched_ids = nneighbors_index_to_id(n_neighbors_index, sources)

    synthetic_population_matched = synthetic_population.copy()
    #print("synthetic population matched")
    synthetic_population_matched["source_id"] = matched_ids.to_list()
    #print(synthetic_population_matched)
    synthetic_population_matched = pd.merge(synthetic_population_matched, sources.loc[:, ["id_ind", "w_ind",
                                                                                          "main_distance",
                                                                                          "main_activity",
                                                                                          "main_activity_name",
                                                                                          "main_transport",
                                                                                          "immo_lun", "immo_mar",
                                                                                          "immo_mer", "immo_jeu",
                                                                                          "immo_ven"]],
                                            left_on="source_id", right_on="id_ind")
    synthetic_population_matched["w_ind"] = 1
    #print(synthetic_population_matched)

    return synthetic_population_matched


def match_and_analyse(synthetic_population, sources, travels_entd,
                      matching_attributes_categorical_emp,
                      matching_attributes_quantitative_emp,
                      matching_attributes_categorical_not_emp,
                      matching_attributes_quantitative_not_emp,
                      nneighbors, radius):
    print("-- match synthetic population with emp sources")

    mask_syn_pop_employed = synthetic_population["status"] == "employed"
    synthetic_population_emp = synthetic_population[mask_syn_pop_employed]
    synthetic_population_not_emp = synthetic_population[~mask_syn_pop_employed]

    mask_sources_employed = sources["status"] == "employed"
    sources_emp = sources[mask_sources_employed]
    sources_not_emp = sources[~mask_sources_employed]

    matched_emp = standardize_and_match(synthetic_population_emp, sources_emp,
                                        matching_attributes_categorical_emp,
                                        matching_attributes_quantitative_emp,
                                        nneighbors, radius)
    matched_not_emp = standardize_and_match(synthetic_population_not_emp, sources_not_emp,
                                            matching_attributes_categorical_not_emp,
                                            matching_attributes_quantitative_not_emp,
                                            nneighbors, radius)
    synthetic_population_matched = pd.concat([matched_emp, matched_not_emp], ignore_index=True)

    """
    print("-- TRAVELS EMPLOYED")
    analysis_emp = analysis_emd(matched_emp, travels_entd, "test", False, True, True)
    print("-- TRAVELS NOT EMPLOYED")
    analysis_not_emp = analysis_emd(matched_not_emp, travels_entd, "test", False, True, True)
    print("-- TRAVELS ALL")
    analysis_all = analysis_emd(synthetic_population_matched, travels_entd, "test", False, True, True)
    
    sources_matched = pd.merge(synthetic_population_matched["source_id"], sources, left_on="source_id",
                               right_on="id_ind")
    comparison(synthetic_population_matched, sources_matched)
    """
    return synthetic_population_matched


def match_synthetic_population_with_entd_sources(synthetic_population,
                                                 sources,
                                                 travels_entd,
                                                 matching_attributes_categorical_emp=attr_cat_emp,
                                                 matching_attributes_quantitative_emp=attr_quant_emp,
                                                 matching_attributes_categorical_not_emp=attr_cat_not_emp,
                                                 matching_attributes_quantitative_not_emp=attr_quant_not_emp,
                                                 nneighbors=40,
                                                 radius=0.3):
    synthetic_population_matched = match_and_analyse(synthetic_population, sources, travels_entd,
                                                     matching_attributes_categorical_emp,
                                                     matching_attributes_quantitative_emp,
                                                     matching_attributes_categorical_not_emp,
                                                     matching_attributes_quantitative_not_emp,
                                                     nneighbors, radius)

    esc = True
    while not esc:
        go = False
        attr = {"emp": {"cat": {}, "quant": {}},
                "not_emp": {"cat": {}, "quant": {}}}
        while not go:
            action = input("'type attr coef', ex: 'emp cat csp 1', 'not_emp quant nb_child 1.5' ? ou 'go' ou 'esc'")
            if action == "go":
                go = True
            elif action == "esc":
                esc = True
            else:
                cmd = action.split(" ")
                if len(cmd) == 4:
                    is_emp, cat_quant, attribute, coef = cmd
                    if is_emp in ["emp", "not_emp"] and cat_quant in ["cat", "quant"] \
                            and attribute in ["status", "sexe", "work_transport", "commune_uu_status", "csp", "age",
                                              "nb_child", "nb_pers", "nb_car", "work_dist", "work_dist_adapted",
                                              "child/adult_is1+", "car/adult_is1+", "commune_density"]:
                        coef = float(coef)
                        attr[is_emp][cat_quant][attribute] = coef
                    else:
                        pass
                else:
                    pass

        nneighbors = int(input("Nombre de voisins ? - default " + str(nneighbors)))
        radius = float(input("Radius ? - default " + str(radius)))

        matching_attributes_cat_emp = matching_attributes_categorical_emp.copy()
        [matching_attributes_cat_emp.update({key: value}) for key, value in attr["emp"]["cat"].items()]
        matching_attributes_quant_emp = matching_attributes_quantitative_emp.copy()
        [matching_attributes_quant_emp.update({key: value}) for key, value in attr["emp"]["quant"].items()]
        matching_attributes_cat_not_emp = matching_attributes_categorical_not_emp.copy()
        [matching_attributes_cat_not_emp.update({key: value}) for key, value in attr["not_emp"]["cat"].items()]
        matching_attributes_quant_not_emp = matching_attributes_quantitative_not_emp.copy()
        [matching_attributes_quant_not_emp.update({key: value}) for key, value in attr["not_emp"]["quant"].items()]

        synthetic_population_matched = match_and_analyse(synthetic_population, sources, travels_entd,
                                                         matching_attributes_cat_emp,
                                                         matching_attributes_quant_emp,
                                                         matching_attributes_cat_not_emp,
                                                         matching_attributes_quant_not_emp,
                                                         nneighbors, radius)
    return synthetic_population_matched
