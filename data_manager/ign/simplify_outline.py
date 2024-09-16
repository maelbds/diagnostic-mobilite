import json
import numpy as np
import matplotlib.pyplot as plt
import topojson as tp

from shapely.geometry import shape, Polygon, MultiPolygon, GeometryCollection


def filter_small_outlines(outlines_shapes):
    def filter_multipolygon(multipolygon):
        multipolygon_properties = multipolygon["properties"]
        multipolygon_geom_shape = shape(multipolygon["geometry"])
        multipolygon_geom = MultiPolygon([p for p in list(multipolygon_geom_shape) if p.area > 0.0001]).__geo_interface__
        return {
            "type": "Feature",
            "properties": multipolygon_properties,
            "geometry": multipolygon_geom
        }
    outlines_shapes_filtered = [filter_multipolygon(s) if s["geometry"]["type"] == "MultiPolygon" else s for s in outlines_shapes]
    return outlines_shapes_filtered


def simplify_outline(outline_shapes, simplify_cursor=0.02):
    """
    :param outline_shapes: list of shapes (GeoJSON Objects)
    :param simplify_cursor:
    :return:
    """
    def plot_shapes(shapes, color=None):
        for s in shapes:
            if s["geometry"]["type"] == "Polygon":
                outline = np.array(s["geometry"]["coordinates"][0])
                lats = outline[:, 0]
                lons = outline[:, 1]
                if color is not None:
                    plt.plot(lats, lons, color)
                else:
                    plt.plot(lats, lons)
            elif s["geometry"]["type"] == "MultiPolygon":
                for p in s["geometry"]["coordinates"]:
                    outline = np.array(p[0])
                    lats = outline[:, 0]
                    lons = outline[:, 1]
                    if color is not None:
                        plt.plot(lats, lons, color)
                    else:
                        plt.plot(lats, lons)

    # display original shapes in blue
    plot_shapes(outline_shapes, "b")
    print(f"Number of shapes : {len(outline_shapes)}")

    # filter small outlines
    #outline_shapes = filter_small_outlines(outline_shapes)

    # create and simplify topology object from shapes
    topo = tp.Topology([s for s in outline_shapes])
    topo.to_json("topo_epci.json")
    topo = topo.toposimplify(
                        epsilon=simplify_cursor,
                        simplify_algorithm='dp',
                        simplify_with='shapely',
                        prevent_oversimplify=True
                    )
    topo.to_json("topo_epci_l.json")

    # back to geojson format
    geojson = json.loads(topo.to_geojson(pretty=True, validate=True, decimals=10))
    topo.to_geojson("geo_epci.json") # to check file size
    light_shapes = geojson["features"]

    # filter small outlines one more time
    light_shapes = filter_small_outlines(light_shapes)

    # display light shapes in colors
    plot_shapes(light_shapes)
    print(f"Number of light shapes : {len(light_shapes)}")

    plt.axis("equal")
    plt.show()

    return light_shapes

