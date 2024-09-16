import pandas as pd
import numpy as np

from sklearn.metrics import pairwise_distances


def calc_estimated_dist(coord1, coord2):
    X = np.array(coord1) / 1000  # km
    Y = np.array(coord2) / 1000  # km
    crow_fly_dist = abs(np.linalg.norm(X - Y))
    # To estimate dist via road
    # "From crow-fly distances to real distances, or the origin of detours, Heran"
    dist = crow_fly_dist * (1.1 + 0.3 * np.exp(-crow_fly_dist / 20))
    return round(dist, 1)


def get_distances_matrix(_from, _to=None):
    ori = pd.DataFrame({"id": _from["id"], "coords": _from["coords_lamb"]})
    ori = ori.set_index("id")

    if _to is not None:
        des = pd.DataFrame({"id": _to["id"], "coords": _to["coords_lamb"]})
        des = des.set_index("id")
    else:
        des = pd.DataFrame({"id": _from["id"], "coords": _from["coords_lamb"]})
        des = des.set_index("id")

    estimated_distances = pd.DataFrame({
        id_to: ori.apply(lambda row: calc_estimated_dist(row["coords"], coord_to), axis=1)
        for id_to, coord_to in zip(des.index, des["coords"])
    })
    return estimated_distances


def crow_fly_to_estimated_dist(crow_fly_dist_km):
    # To estimate dist via road
    # "From crow-fly distances to real distances, or the origin of detours, Heran"
    dist = crow_fly_dist_km * (1.1 + 0.3 * np.exp(-crow_fly_dist_km / 20))
    return dist


def compute_distance_matrix(X, Y=None):
    X_coords = X["coords_lamb"].tolist()
    X_ids = X["id"].to_list()

    if Y is not None:
        Y_coords = Y["coords_lamb"].tolist()
        Y_ids = Y["id"].to_list()
    else:
        Y_coords = X["coords_lamb"].tolist()
        Y_ids = X["id"].to_list()

    if len(Y_ids) > 0:
        matrix = pairwise_distances(X_coords, Y_coords)

        # complete distance with same origin and destination with attribute inner_dist
        for i in range(len(X)):
            id_X = X_ids[i]
            if id_X in Y_ids:
                j = Y_ids.index(id_X)
                matrix[i, j] = X["inner_dist"].iloc[i]

        matrix = matrix / 1000  # to km
        matrix = np.vectorize(crow_fly_to_estimated_dist)(matrix)
        matrix = np.round(matrix, 2)

        matrix = pd.DataFrame(matrix, index=X_ids, columns=Y_ids)
    else:
        matrix = pd.DataFrame(index=X_ids)
    return matrix

