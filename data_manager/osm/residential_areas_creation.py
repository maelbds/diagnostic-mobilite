"""
To identify residential areas within a commune based on OSM data

https://wiki.openstreetmap.org/wiki/Key:landuse
https://wiki.openstreetmap.org/wiki/Key:building
https://wiki.openstreetmap.org/wiki/Key:amenity
"""

import pprint
import numpy as np
import matplotlib.pyplot as plt

from data_manager.insee_filosofi.gridded_population import get_gridded_population
from data_manager.osm.api_request import api_osm_request_center, api_osm_request_geom
from data_manager.osm.functions_format import light_osm_data_geom, light_osm_data_center, process_osm_data_places
from data_manager.osm.functions_geometry import is_point_in_polygon, create_outline
from data_manager.osm.functions_geography import distance_pt_pt
from data_manager.osm.cluster import create_buildings_cluster, create_gridded_pop_cluster


def get_buildings(geo_code):
    buildings = api_osm_request_center(geo_code, "building", ["yes"])
    return buildings


def get_areas_names(geo_code):
    areas = api_osm_request_center(geo_code, "place", ["hamlet", "village", "neighbourhood", "quarter", "suburb"])
    return areas


def get_non_residential_areas(geo_code):
    nr_areas = api_osm_request_geom(geo_code, "landuse", ["commercial",
                                                          "construction",
                                                          "industrial",
                                                          "retail",
                                                          "military",
                                                          "depot",
                                                          "garages",
                                                          "port",
                                                          "recreation_ground",
                                                          "religious"])
    return nr_areas


# -----------------------------------------------------------------------------


def get_residential_buildings(geo_code):
    """
    Get coordinates of all residential buildings by getting all buildings and removing ones not in residential areas
    :param geo_code: (Int) INSEE geo_code of concerned commune
    :return: (List) of coordinates of all residential buildings
    """
    buildings = get_buildings(geo_code)
    non_residential_areas = get_non_residential_areas(geo_code)

    light_buildings = light_osm_data_center(buildings)
    light_non_residential_areas = light_osm_data_geom(non_residential_areas)

    residential_buildings = [b for b in light_buildings if not True in
                                                               [is_point_in_polygon(b, n_ra) for n_ra in
                                                                light_non_residential_areas]]
    return residential_buildings


def get_name(areas_names, point):
    """
    Get name of point among given areas names. Selected name is the closest one if distance below distance_threshold
    :param areas_names: (JSON) names from osm api
    :param point:  [lat, lon]
    :return: (String) name of point or None if not found
    """
    distance_threshold = 500  # meters

    if len(areas_names) == 0:
        return None

    names = [an["name"] for an in areas_names]
    coords = [[an["lat"], an["lon"]] for an in areas_names]

    distances = [distance_pt_pt(point, coord) for coord in coords]

    min_dist = min(distances)
    if min_dist < distance_threshold:
        return names[distances.index(min_dist)]
    else:
        return None


# -----------------------------------------------------------------------------


def create_residential_areas(geo_code):
    """
    Get the residential areas within the commune with given geocode
    :param geo_code: (Int) INSEE geo_code of concerned commune
    :return: (List) of the residential areas with their [name, center_coords, nb_buildings, outline]
    """
    print(f"Get residential areas for geo_code {geo_code}")
    residential_areas = []

    print("--- get residential buildings")
    residential_buildings = get_residential_buildings(geo_code)
    if residential_buildings == []:
        return residential_areas

    print("--- get areas names")
    areas_names = process_osm_data_places(get_areas_names(geo_code), "residential")

    print("--- create clusters")
    # Parameters for global clustering (villages) - do not change
    global_threshold_m = 200  # meters
    # Parameters for local clustering (dense areas) - do not change
    local_threshold_m = 10000  # meters
    # Min number of buildings to keep a cluster
    min_nb_of_buildings_inside_cluster = 20
    clusters = create_buildings_cluster(residential_buildings,
                                        global_threshold_m,
                                        local_threshold_m,
                                        min_nb_of_buildings_inside_cluster)

    print("--- create residential areas")
    index = 0
    for c in clusters:
        center = list(np.mean(c, axis=0))
        outline = create_outline(c)
        buildings_nb = len(c)
        name = get_name(areas_names, center)
        if name is None:
            name = "residential_area_" + str(index)
            index += 1
        residential_areas.append([name, center, buildings_nb, outline])

    if __name__ == "__main__":
        display_clusters(clusters)

    return residential_areas


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


# ---------------------------------------------------------------------


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

    if __name__ == "__main__":
        display_clusters([[c["coords"] for c in cluster] for cluster in clusters])

    return residential_areas



# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    gridded_pop = get_gridded_population(None, "84133")
    pprint.pprint(create_residential_areas_from_gridded_pop(gridded_pop))
