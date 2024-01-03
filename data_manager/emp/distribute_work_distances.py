import numpy as np

from sklearn.preprocessing import OneHotEncoder

from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler


def find_distances(to_match, sources, n_neighbors=10):
    sources["pond_indC"] = sources["pond_indC"].astype("float64")

    std_X, std_samples = prepare_data_for_nneighbors(to_match, sources)
    n_neighbors_index = find_nneighbors(std_X, std_samples, n_neighbors)
    matched_indexes = nneighbors_indexes_to_index(n_neighbors_index, sources)

    distances = sources.iloc[matched_indexes]["__work_dist"].tolist()
    modes = sources.iloc[matched_indexes]["__work_transport"].tolist()
    return distances, modes


def prepare_data_for_nneighbors(to_match, sources):
    to_match["__work_transport"] = to_match["__work_transport"].fillna("Z")
    sources["__work_transport"] = sources["__work_transport"].fillna("Z")

    cat_attr = ["SEXE", "__csp", "STATUTCOM_UU_RES"]
    quant_attr = ["AGE", "NPERS", "NENFANTS", "JNBVEH"]

    # prepare data
    min_max_scaler = MinMaxScaler()
    one_hot = OneHotEncoder()

    # print("-- standardize sources = samples")
    sources_quant = sources.loc[:, quant_attr].fillna(1000).astype("int32")
    std_sources_quant = sources_quant.to_numpy()
    minmax_sources_quant = min_max_scaler.fit_transform(std_sources_quant)

    sources_cat = sources.loc[:, cat_attr]
    onehot_sources_cat = one_hot.fit_transform(sources_cat.to_numpy()).toarray()

    std_samples = np.concatenate((minmax_sources_quant, onehot_sources_cat), axis=1)

    # print("-- standardize persons to match")
    to_match_quant = to_match.loc[:, quant_attr].fillna(1000).astype("int32")
    std_to_match_quant = to_match_quant.to_numpy()
    minmax_to_match_quant = min_max_scaler.transform(std_to_match_quant)

    to_match_cat = to_match.loc[:, cat_attr]
    onehot_to_match_cat = one_hot.transform(to_match_cat.to_numpy()).toarray()

    std_X = np.concatenate((minmax_to_match_quant, onehot_to_match_cat), axis=1)
    return std_X, std_samples


def find_nneighbors(std_X, std_samples, nneighbors):
    # print("-- compute nearest neighbors")
    neigh = NearestNeighbors(n_neighbors=nneighbors, radius=0.1, metric="manhattan")
    neigh.fit(std_samples)

    r_neighbors_dist, r_neighbors_index = neigh.radius_neighbors(std_X, return_distance=True)
    n_neighbors_dist, n_neighbors_index = neigh.kneighbors(std_X, return_distance=True)

    neighbors_index = [ri if len(ri) >= nneighbors else ni for ri, ni in zip(r_neighbors_index, n_neighbors_index)]

    neighbors_dist = np.array([[np.mean(rd)] * nneighbors if len(rd) >= nneighbors else nd for rd, nd in
                               zip(r_neighbors_dist, n_neighbors_dist)])
    neighbors_r_n = [True if len(ri) >= nneighbors else False for ri, ni in
                     zip(r_neighbors_index, n_neighbors_index)]
    return neighbors_index


def nneighbors_indexes_to_index(n_neighbors_index, sources):
    def indexes_to_index(indexes):
        weights = sources.iloc[indexes]["pond_indC"]
        ind = np.random.choice(indexes, p=weights/weights.sum())
        return ind

    matched_indexes = [indexes_to_index(indexes) for indexes in n_neighbors_index]
    return matched_indexes