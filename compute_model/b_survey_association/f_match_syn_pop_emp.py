import pandas as pd
import numpy as np

from sklearn.preprocessing import OneHotEncoder


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

    matching_attributes_quantitative = {attr: coef for attr, coef in matching_attributes_quantitative.items() if
                                        coef > 0}
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

    # print("-- find nearest neighbors")
    r_neighbors_dist, r_neighbors_index = neigh.radius_neighbors(std_X, return_distance=True)
    n_neighbors_dist, n_neighbors_index = neigh.kneighbors(std_X, return_distance=True)

    neighbors_index = [ri if len(ri) >= nneighbors else ni for ri, ni in zip(r_neighbors_index, n_neighbors_index)]
    return neighbors_index


def nneighbors_index_to_id(n_neighbors_index, sources):
    def indexes_to_ind(indexes):
        weights = sources.iloc[indexes]["w_ind"]
        ind = np.random.choice(indexes, p=weights / weights.sum())
        return ind

    matched_indexes = [indexes_to_ind(indexes) for indexes in n_neighbors_index]
    matched_ids = sources.iloc[matched_indexes]["id_ind"]
    return matched_ids


def standardize_and_match(synthetic_population, sources, matching_attributes_categorical,
                          matching_attributes_quantitative,
                          nneighbors, radius):
    std_X, std_samples, min_max_scaler = prepare_data_for_nneighbors(synthetic_population, sources,
                                                                     matching_attributes_categorical,
                                                                     matching_attributes_quantitative)

    n_neighbors_index = find_nneighbors(std_X, std_samples, nneighbors, radius)
    matched_ids = nneighbors_index_to_id(n_neighbors_index, sources)

    synthetic_population_matched = synthetic_population.copy()
    # print("synthetic population matched")
    synthetic_population_matched["source_id"] = matched_ids.to_list()
    # print(synthetic_population_matched)
    synthetic_population_matched = pd.merge(synthetic_population_matched,
                                            sources.loc[:, ["id_ind", "w_ind", "main_distance", "main_activity",
                                                            "main_activity_name", "main_transport",
                                                            "immo_lun", "immo_mar", "immo_mer", "immo_jeu", "immo_ven"]],
                                            left_on="source_id", right_on="id_ind")
    synthetic_population_matched = synthetic_population_matched.drop(columns=["id_ind_y"]).rename(columns={"id_ind_x": "id_ind"})
    synthetic_population_matched["w_ind"] = 1

    return synthetic_population_matched


def match_syn_pop_with_emp(synthetic_population,
                           emp,
                           matching_attributes_categorical_employed=attr_cat_emp,
                           matching_attributes_quantitative_employed=attr_quant_emp,
                           matching_attributes_categorical_not_employed=attr_cat_not_emp,
                           matching_attributes_quantitative_not_employed=attr_quant_not_emp,
                           nneighbors=40,
                           radius=0.3):

    mask_syn_pop_employed = synthetic_population["status"] == "employed"
    synthetic_population_emp = synthetic_population[mask_syn_pop_employed]
    synthetic_population_not_emp = synthetic_population[~mask_syn_pop_employed]

    mask_sources_employed = emp["status"] == "employed"
    sources_employed = emp[mask_sources_employed]
    sources_not_employed = emp[~mask_sources_employed]

    matched_employed = standardize_and_match(synthetic_population_emp, sources_employed,
                                             matching_attributes_categorical_employed,
                                             matching_attributes_quantitative_employed,
                                             nneighbors, radius)
    matched_not_employed = standardize_and_match(synthetic_population_not_emp, sources_not_employed,
                                                 matching_attributes_categorical_not_employed,
                                                 matching_attributes_quantitative_not_employed,
                                                 nneighbors, radius)
    synthetic_population_matched = pd.concat([matched_employed, matched_not_employed], ignore_index=True)

    return synthetic_population_matched
