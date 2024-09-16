"""
Functions to create clusters

Course : https://openclassrooms.com/fr/courses/4379436-explorez-vos-donnees-avec-des-algorithmes-non-supervises/4379561-partitionnez-vos-donnees-avec-un-algorithme-de-clustering-hierarchique
Library doc : https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html
"""
import pprint
import matplotlib.pyplot as plt

import numpy as np
from sklearn.cluster import AgglomerativeClustering, DBSCAN


def cluster_single(list_to_cluster, distance_threshold):
    """
    To create cluster with single linkage - used to cluster villages

    :param list_to_cluster: (List) of coordinates ([lat, lon])
    :param distance_threshold:
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
    print(len(X))
    if len(X) > 1:
        clustering = AgglomerativeClustering(n_clusters=None,
                                             linkage="ward",
                                             distance_threshold=distance_threshold).fit(X)
        return clustering.labels_
    else:
        return np.array([0])


def cluster_dbscan(list_to_cluster, weights, distance_threshold):
    """
    To create cluster with ward linkage - used to cluster within a dense zone

    :param list_to_cluster: (List) of coordinates ([lat, lon])
    :param distance_threshold:
    :return: (List) of cluster labels
    """
    X = np.array(list_to_cluster)
    if len(X) > 1:
        clustering = DBSCAN(eps=distance_threshold, min_samples=50).fit(X, sample_weight=weights)
        return clustering.labels_
    else:
        return np.array([0])


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


def display_clusters(clusters, centers=None):
    for c in clusters:
        coords = np.array(c)
        plt.plot(coords[:, 0], coords[:, 1], 'o', markersize=2)
    if centers is not None:
        i = 0
        for coords in centers:
            i += 1
            plt.plot(coords[0], coords[1], "x", markersize=i)
    plt.axis('equal')
    plt.show()
