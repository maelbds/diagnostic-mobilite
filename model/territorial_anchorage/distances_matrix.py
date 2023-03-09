import pandas as pd
import numpy as np

from model.functions.osrm import itinerary_osrm


def get_distances_matrix(_from, _to):
    _from = pd.DataFrame({"id": [f.id for f in _from], "coords": [f.coords for f in _from]})
    _from = _from.set_index("id")
    _to = pd.DataFrame({"id": [f.id for f in _to], "coords": [f.coords for f in _to]})
    _to = _to.set_index("id")

    def calc_estimated_dist(coord1, coord2):
        X = np.array(coord1)
        Y = np.array(coord2)
        conv_deg_km = np.array([np.pi / 180 * 6400, np.pi / 180 * 4400])
        crow_fly_dist = abs(np.linalg.norm(np.multiply(X - Y, conv_deg_km)))
        # To estimate dist via road
        # "From crow-fly distances to real distances, or the origin of detours, Heran"
        dist = crow_fly_dist * (1.1 + 0.3 * np.exp(-crow_fly_dist / 20))
        return dist

    estimated_distances = pd.DataFrame({
        id_to: _from.apply(lambda row: calc_estimated_dist(row["coords"], coord_to), axis=1)
        for id_to, coord_to in zip(_to.index, _to["coords"])
    })
    return estimated_distances


def get_distances_matrix_areas(areas):
    areas_df = pd.DataFrame([a.to_dict_distance_matrix() for a in areas])
    areas_df = areas_df.set_index("id")

    def calc_estimated_dist(coord1, coord2):
        X = np.array(coord1)
        Y = np.array(coord2)
        conv_deg_km = np.array([np.pi / 180 * 6400, np.pi / 180 * 4400])
        crow_fly_dist = abs(np.linalg.norm(np.multiply(X - Y, conv_deg_km)))
        # To estimate dist via road
        # "From crow-fly distances to real distances, or the origin of detours, Heran"
        dist = crow_fly_dist * (1.1 + 0.3 * np.exp(-crow_fly_dist / 20))
        return dist

    def calc_osrm_dist(coord1, coord2):
        return itinerary_osrm(coord1, coord2)["distance"]

    estimated_distances = pd.DataFrame({
        id2: areas_df.apply(lambda row: calc_estimated_dist(row["coords"], coord2), axis=1)
        for id2, coord2 in zip(areas_df.index, areas_df["coords"])
    })
    """
    osrm_distances = pd.DataFrame({
        id2: areas_df.apply(lambda row: calc_osrm_dist(row["coord"], coord2), axis=1)
        for id2, coord2 in zip(areas_df["id"], areas_df["coord"])
    })
    """
    return estimated_distances


def build_distances_matrix_communes(communes):
    communes_df = pd.DataFrame([c.to_dict_distance_matrix() for c in communes])
    communes_df = communes_df.set_index("geo_code")

    def calc_estimated_dist(coord1, coord2):
        X = np.array(coord1)
        Y = np.array(coord2)
        conv_deg_km = np.array([np.pi / 180 * 6400, np.pi / 180 * 4400])
        crow_fly_dist = abs(np.linalg.norm(np.multiply(X - Y, conv_deg_km)))
        # To estimate dist via road
        # "From crow-fly distances to real distances, or the origin of detours, Heran"
        dist = crow_fly_dist * (1.1 + 0.3 * np.exp(-crow_fly_dist / 20))
        return dist

    estimated_distances = pd.DataFrame({
        id2: communes_df.apply(lambda row: calc_estimated_dist(row["coords"], coord2), axis=1)
        for id2, coord2 in zip(communes_df.index, communes_df["coords"])
    })
    return estimated_distances


