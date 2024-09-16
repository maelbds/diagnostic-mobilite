"""
Functions used in osm/ related to geometry
"""
import numpy as np
from scipy.spatial import ConvexHull
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


def is_point_in_polygon(point, polygon):
    """
    Check if point is in polygon
    :param point: (List) Point coordinates [lat, lon]
    :param polygon: (List) of points coordinates [[lat, lon]]
    :return: Boolean
    """
    point = Point(point)
    polygon = Polygon(polygon)
    if polygon.contains(point):
        return True
    else:
        return False


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

