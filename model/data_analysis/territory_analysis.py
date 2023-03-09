import pandas as pd

from data_manager.dictionnary.places_categories import get_places_categories
from model.area import ClusterArea
from model.functions.cluster import cluster_single, cluster_ward, split_clustered_data


def get_areas_by_category(areas):
    categories = {area.category: area.category_fr for area in areas}
    areas_by_category = [{
        "name": name,
        "name_fr": name_fr,
        "areas": [area.to_dict_output() for area in areas if area.category == name]
    } for name, name_fr in categories.items()]
    return areas_by_category


def get_areas_by_reason(areas):
    reasons = {area.reason: area.reason_fr for area in areas}
    areas_by_reason = [{
        "name": name,
        "name_fr": name_fr,
        "areas": [area.to_dict_output() for area in areas if area.reason == name]
    } for name, name_fr in reasons.items()]
    return areas_by_reason


def build_activity_zones(territory):
    def create_cluster(places, commune,
                       clustering_distance_single=0.5,
                       clustering_distance_ward=7,
                       min_nb_of_items_inside_cluster=2):
        places_coords = [p.coords for p in places]
        if len(places_coords) > 1:
            labels = cluster_single(places_coords, clustering_distance_single)
            global_clusters = split_clustered_data(places, labels)

            local_clusters = []
            for gc in global_clusters:
                if len(gc) > min_nb_of_items_inside_cluster:
                    gc_coords = [p.coords for p in gc]
                    labels_local = cluster_ward(gc_coords, clustering_distance_ward)
                    cluster_local = split_clustered_data(gc, labels_local)
                    for cl in cluster_local:
                        if len(cl) > min_nb_of_items_inside_cluster:
                            local_clusters.append(cl)

            return [ClusterArea(c, commune) for c in local_clusters]
        else:
            return []

    activity_cluster_areas = []

    for c in territory.communes + territory.influence_communes + territory.work_communes:
        characteristic_places = [p for p in c.places if p.characteristic]
        activity_cluster_areas.extend(
            create_cluster(characteristic_places, c)
        )

    places_categories = get_places_categories()

    def filter_cluster_area(cluster_area):
        places_categories['types'] = [[] for _ in range(len(places_categories))]
        categories = places_categories.set_index("name").drop(columns=["name_fr", "id_reason"]).to_dict("index")
        [categories[p.category]["types"].append(p.type)
         for p in cluster_area.places
         if p.type not in categories[p.category]["types"]]

        if sum([len(value["types"]) >= value["characteristic_level_2"] for category, value in categories.items()]) \
                == len(categories.keys()):
            cluster_area.level = 2
            return True
        elif sum([len(value["types"]) >= value["characteristic_level_1"] for category, value in categories.items()]) \
                >= len(categories.keys()) - 1 or len(cluster_area.places) > 40:
            cluster_area.level = 1
            return True
        elif sum([len(value["types"]) >= value["characteristic_level_0"] for category, value in categories.items()]) \
                >= len(categories.keys()) - 1 and len(cluster_area.places) > 3:
            cluster_area.level = 0
            return True
        else:
            return False

    activity_cluster_areas = [ca for ca in activity_cluster_areas if filter_cluster_area(ca)]
    return activity_cluster_areas


