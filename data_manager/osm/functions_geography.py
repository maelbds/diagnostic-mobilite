"""
Functions used in osm/ related to geography
"""
import numpy as np

earth_radius = 6400000  # meters
radius_france = 4400000  # meters


def distance_pt_pt(a, b):
    """
    Compute the distance (meters) between two points (coordinates).
    SIMPLIFIED COMPUTATION, ONLY FOR CLOSE POINTS IN FRANCE.
    :param a: (List) point [a_lat, a_lon]
    :param b: (List) point [b_lat, b_lon]
    :return: (Float) distance between the two points (meters)
    """
    X = np.array(a)
    Y = np.array(b)
    conv_deg_km = np.array([
        np.pi / 180 * earth_radius,  # latitude degrees to meters
        np.pi / 180 * radius_france  # longitude degrees to meters
    ])
    return abs(np.linalg.norm(np.multiply(X - Y, conv_deg_km)))

