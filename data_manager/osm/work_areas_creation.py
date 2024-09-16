"""
To identify work areas within a commune based on OSM data

https://wiki.openstreetmap.org/wiki/Key:landuse
https://wiki.openstreetmap.org/wiki/Key:building
https://wiki.openstreetmap.org/wiki/Key:amenity
"""

import pprint
import numpy as np
import matplotlib.pyplot as plt

from data_manager.osm.api_request import api_osm_request_center, api_osm_request_geom
from data_manager.osm.functions_format import light_osm_data_geom, light_osm_data_center, process_osm_data_places
from data_manager.osm.functions_geometry import is_point_in_polygon, create_outline
from data_manager.osm.functions_geography import distance_pt_pt
from data_manager.osm.cluster import create_buildings_cluster


def get_buildings(geo_code):
    buildings = api_osm_request_center(geo_code, "building", ["yes"])
    return buildings


def get_work_areas(geo_code):
    work_areas = api_osm_request_geom(geo_code, "landuse", ["commercial", "industrial", "retail"])
    return work_areas


def get_areas_names(geo_code):
    areas = api_osm_request_center(geo_code, "place", ["hamlet", "village", "neighbourhood", "quarter", "suburb"])
    return areas


# -----------------------------------------------------------------------------


def get_work_buildings(geo_code):
    """
    Get coordinates of all residential buildings by getting all buildings and removing ones not in residential areas
    :param geo_code: (Int) INSEE geo_code of concerned commune
    :return: (List) of coordinates of all residential buildings
    """
    buildings = get_buildings(geo_code)
    work_areas = get_work_areas(geo_code)

    light_buildings = light_osm_data_center(buildings)
    light_work_areas = light_osm_data_geom(work_areas)

    work_buildings = [b for b in light_buildings if True in
                      [is_point_in_polygon(b, wa) for wa in light_work_areas]]

    return work_buildings


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


def create_work_areas(geo_code):
    """
    Get the work areas within the commune with given geocode
    :param geo_code: (Int) INSEE geo_code of concerned commune
    :return: (List) of the work areas with their [name, center_coords, nb_buildings, outline]
    """
    print(f"Get work areas for geo_code {geo_code}")
    work_areas = []

    print("--- get work buildings")
    work_buildings = get_work_buildings(geo_code)
    if work_buildings == []:
        work_areas.append([None, [None, None], 0])
        return work_areas

    print("--- get areas names")
    areas_names = process_osm_data_places(get_areas_names(geo_code), "work")

    print("--- create clusters")
    # Parameter for global clustering (zones) - do not change
    global_threshold_m = 150  # meters
    # Parameter for local clustering (dense areas) - do not change
    local_threshold_m = 10000  # meters
    # Min number of buildings to keep a cluster
    min_nb_of_buildings_inside_cluster = 5
    clusters = create_buildings_cluster(work_buildings,
                                        global_threshold_m,
                                        local_threshold_m,
                                        min_nb_of_buildings_inside_cluster)
    if len(clusters) == 0:
        work_areas.append([None, [None, None], 0])
        return work_areas

    print("--- create work areas")
    index = 0
    for c in clusters:
        center = np.mean(c, axis=0)
        buildings_nb = len(c)
        name = get_name(areas_names, center)
        if name is None:
            name = "work_area_" + str(index)
            index += 1
        work_areas.append([name, center, buildings_nb])

    if __name__ == "__main__":
        display_clusters(clusters)

    return work_areas


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


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pprint.pprint(create_work_areas(79189))
