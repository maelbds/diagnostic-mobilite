"""
Functions to create clusters

Course : https://openclassrooms.com/fr/courses/4379436-explorez-vos-donnees-avec-des-algorithmes-non-supervises/4379561-partitionnez-vos-donnees-avec-un-algorithme-de-clustering-hierarchique
Library doc : https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html
"""
import pprint

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt

from data_manager.insee_filosofi.gridded_population import get_gridded_population


def cluster_single(list_to_cluster, distance_threshold):
    """
    To create cluster with single linkage - used to cluster places

    :param list_to_cluster: (List) of coordinates ([lat, lon])
    :param distance_threshold: meters
    :return: (List) of cluster labels
    """
    X = np.array(list_to_cluster)
    if len(X) > 1:
        clustering = AgglomerativeClustering(n_clusters=None,
                                             linkage="single",
                                             distance_threshold=distance_threshold).fit(X)
        return clustering.labels_
    else:
        return np.array([0])


def cluster_ward(list_to_cluster, distance_threshold):
    """
    To create cluster with ward linkage - used to cluster within a dense zone

    :param list_to_cluster: (List) of coordinates ([lat, lon])
    :param distance_threshold:
    :return: (List) of cluster labels
    """
    X = np.array(list_to_cluster)
    if len(X) > 1:
        clustering = AgglomerativeClustering(n_clusters=None,
                                             linkage="ward",
                                             distance_threshold=distance_threshold).fit(X)
        return clustering.labels_
    else:
        return np.array([0])


def create_cluster(buildings, global_threshold_m, local_threshold_m, min_nb_of_items_inside_cluster):
    """
    Clustering process is divided in two steps :
    1. Global clustering to identify villages/cities with single clustering method
    2. Local clustering to cluster within villages/cities with ward clustering method
    :param buildings: (List) of coordinates of buildings
    :param global_threshold_m: (Int) threshold value for step 1
    :param local_threshold_m: (Int) threshold value for step 2
    :return: (List) of coordinates of buildings, splitted into clusters
    """
    earth_radius = 6400000  # meters

    global_threshold_rad = global_threshold_m / earth_radius * 180 / np.pi
    local_threshold_rad = local_threshold_m / earth_radius * 180 / np.pi

    labels = cluster_single(buildings, global_threshold_rad)
    global_clusters = split_clustered_data(buildings, labels)

    local_clusters = []
    for gc in global_clusters:
        if len(gc) > min_nb_of_items_inside_cluster:
            labels_local = cluster_ward(gc, local_threshold_rad)
            cluster_local = split_clustered_data(gc, labels_local)
            for cl in cluster_local:
                if len(cl) > min_nb_of_items_inside_cluster:
                    local_clusters.append(cl)

    return local_clusters


def split_clustered_data(data, labels):
    """
    Split data list according to labels values
    :param data: (List) of data
    :param labels: (List) of labels get with cluster function
    :return: (List) of data splitted according to labels values
    """
    nb_clusters = max(labels) + 1
    # creation of empty list of list
    clusters = [[] for i in range(nb_clusters)]
    # separation of clusters
    for i in range(len(labels)):
        clusters[labels[i]].append(data[i])
    return clusters


def create_gridded_pop_cluster(gridded_pop, global_threshold_m, local_threshold_m, min_population_inside_cluster):
    """
    Clustering process is divided in two steps :
    1. Global clustering to identify villages/cities with single clustering method
    2. Local clustering to cluster within villages/cities with ward clustering method
    :param buildings: (List) of coordinates of buildings
    :param global_threshold_m: (Int) threshold value for step 1
    :param local_threshold_m: (Int) threshold value for step 2
    :return: (List) of coordinates of buildings, splitted into clusters
    """
    earth_radius = 6400000  # meters

    global_threshold_rad = global_threshold_m / earth_radius * 180 / np.pi
    local_threshold_rad = local_threshold_m / earth_radius * 180 / np.pi

    gridded_pop_coordinates = [g["coords"]for g in gridded_pop]

    labels = cluster_single(gridded_pop_coordinates, global_threshold_rad)
    global_clusters = split_clustered_data(gridded_pop, labels)

    local_clusters = []
    for gc in global_clusters:
        if sum([float(g["population"]) for g in gc]) > min_population_inside_cluster:
            gc_coordinates = [g["coords"] for g in gc]
            labels_local = cluster_ward(gc_coordinates, local_threshold_rad)
            cluster_local = split_clustered_data(gc, labels_local)
            for cl in cluster_local:
                if sum([float(g["population"]) for g in cl]) > min_population_inside_cluster:
                    local_clusters.append(cl)

    return local_clusters


def create_residential_areas_from_gridded_pop(gridded_pop):
    residential_areas = []

    print("--- create clusters")
    # Parameters for global clustering (villages) - do not change
    global_threshold_m = 300  # meters
    # Parameters for local clustering (dense areas) - do not change
    local_threshold_m = 5000  # meters
    # Min number of population to keep a cluster
    min_nb_of_population_inside_cluster = 20

    clusters = create_gridded_pop_cluster(gridded_pop,
                                        global_threshold_m,
                                        local_threshold_m,
                                        min_nb_of_population_inside_cluster)

    print("--- create residential areas")
    index = 0
    for c in clusters:
        c_coords = [ci["coords"] for ci in c]
        center = list(np.mean(c_coords, axis=0))
        outline = create_outline(c_coords)
        pop = sum([float(ci["population"]) for ci in c])
        name = "residential_area_" + str(index)
        index += 1
        residential_areas.append([name, center, pop, outline])

    if __name__ == '__main__':
        display_clusters([[c["coords"] for c in cluster] for cluster in clusters])

    return residential_areas


# ---------------------------------------------------------------------------


def create_outline(points_cloud):
    """
    Create an outline of a points cloud
    :param points_cloud: (List) of points [lat, lon]
    :return: (List) of points of the outline [lat, lon]
    """
    if len(points_cloud) < 3:
        outline = points_cloud
    else:
        points_cloud = np.array(points_cloud)
        hull = ConvexHull(points_cloud)
        ind = hull.vertices
        outline = points_cloud[ind]
        outline = [list(o) for o in outline]
    return outline


# -----------------------------------------------------------------------------


def display_clusters(clusters):
    for c in clusters:
        coords = np.array(c)
        plt.plot(coords[:, 1], coords[:, 0], 'o', markersize=2)
    plt.title('Buildings')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.axis('equal')
    plt.show()


if __name__ == "__main__":
    gridded_pop = get_gridded_population(None, "79048")
    pprint.pprint(create_residential_areas_from_gridded_pop(gridded_pop))
