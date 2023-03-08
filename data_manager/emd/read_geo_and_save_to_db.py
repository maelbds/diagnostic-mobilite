import pandas as pd
from sqlite3 import connect
import pprint
import json
import matplotlib.pyplot as plt
import numpy as np
import shapefile
from pyproj import Transformer
from shapely import geometry, wkb

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.insee_general.code_geo_postal import name_to_geo_code


def save_geo(zones):
    def define_cols_values_request(obj):
        return "(" + ", ".join([col for col in obj.columns]) + ")",\
               "(" + ", ".join(["?" for col in obj.columns]) + ")"

    def request(cur, cols, cols_name, values_name):
        cur.execute("""INSERT INTO emd_geo """ + cols_name + """ VALUES """ + values_name, cols)

    # geometry to wkb
    def geojson_to_wkb_geometry_collection(geo):
        geom = geometry.shape(geo)
        geom_coll = geometry.GeometryCollection([geom])
        geom_wkb = wkb.dumps(geom_coll)
        return geom_wkb

    zones["geometry"] = zones["geometry"].apply(lambda geo: geojson_to_wkb_geometry_collection(geo))
    print(zones)

    print("Saving dataset")
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name, values_name = define_cols_values_request(zones)
    [request(cur, list(row.values), cols_name, values_name) for index, row in zones.iterrows()]

    conn.commit()
    conn.close()
    print("Dataset saved")
    return


def read_geojson(dataset_name, coords_system, is_lat_lon, encoding="UTF-8"):
    with open("data/" + dataset_name + "/geo/zones_fines_points.geojson", encoding=encoding) as data:
        geo = json.load(data)
    zones = []

    if coords_system != "epsg:4326":
        transformer = Transformer.from_crs(coords_system,
                                           "epsg:4326")  # World Geodetic System (lat/lon)

    for z in geo["features"]:
        coords_lat_lon = []
        if coords_system != "epsg:4326":
            if z["geometry"]["type"] == "MultiPolygon":
                coords_lat_lon = [[[transformer.transform(coords[0], coords[1]) for coords in points]
                                   for points in polygon] for polygon in z["geometry"]["coordinates"]]
            elif z["geometry"]["type"] == "Polygon":
                coords_lat_lon = [[transformer.transform(coords[0], coords[1]) for coords in polygon] for polygon in z["geometry"]["coordinates"]]
            elif z["geometry"]["type"] == "Point":
                coords_lat_lon = transformer.transform(z["geometry"]["coordinates"][0],
                                                       z["geometry"]["coordinates"][1])
            else:
                print(z["geometry"]["type"])
        else:
            coords_lat_lon = z["geometry"]["coordinates"]

        if not is_lat_lon:
            if z["geometry"]["type"] == "MultiPolygon":
                coords_lat_lon = [[[(coords[1], coords[0]) for coords in points]
                                   for points in polygon] for polygon in coords_lat_lon]
            elif z["geometry"]["type"] == "Polygon":
                coords_lat_lon = [[(coords[1], coords[0]) for coords in polygon] for polygon in coords_lat_lon]
            elif z["geometry"]["type"] == "Point":
                coords_lat_lon = [coords_lat_lon[1], coords_lat_lon[0]]
            else:
                print(z["geometry"]["type"])
        geom = z["geometry"]
        geom["coordinates"] = coords_lat_lon

        zone = {
            "id": z["properties"]["ZF2015_Nou"],
            "name": z["properties"]["Lib_Zone_f"],
            "name_com": z["properties"]["Nom_Com"],
            "geo_code": z["properties"]["DepCom"],
            "geometry": geom
        }
        zones.append(zone)

    for z in zones:
        if z["geometry"]["type"] == "MultiPolygon":
            for polygon in z["geometry"]["coordinates"]:
                outline = np.array(polygon[0])
                lats = outline[:, 0]
                lons = outline[:, 1]
                plt.plot(lons, lats)
        elif z["geometry"]["type"] == "Point":
            coords = z["geometry"]["coordinates"]
            plt.plot(coords[1], coords[0], "o")
        else:
            polygon = z["geometry"]["coordinates"]
            outline = np.array(polygon[0])
            lats = outline[:, 0]
            lons = outline[:, 1]
            plt.plot(lons, lats)
    plt.axis("equal")
    plt.show()

    zones = pd.DataFrame(zones)
    zones["emd_id"] = dataset_name

    # specific to marseille
    """
    zones["id"] = [id.replace(" ", "")[:6] for id in zones["id"]]
    """

    # specific to montpellier
    """
    mask_missing_geo_codes = zones["geo_code"].str.len() == 3
    print(zones)
    print(zones[mask_missing_geo_codes])
    zones.loc[mask_missing_geo_codes, "geo_code"] = zones.loc[mask_missing_geo_codes, "name_com"].apply(
        lambda name: name_to_geo_code(name, ["34", "11", "30", "13", "48"]))
    """

    zones = zones.drop(columns=["name_com"])
    return zones


def read_shp_outlines(dataset_name, coords_system, is_lat_lon, encoding="UTF-8"):
    sf = shapefile.Reader("data/"+ dataset_name + "/geo/zones_fines_points")

    print(sf.records())
    print(sf.fields)

    communes_geo = [r.__geo_interface__ for r in sf.shapeRecords()]

    communes_outlines = pd.DataFrame([{"geo_code": c["properties"]["DepCom"],
                                       "name": c["properties"]["NOM_ZF"],
                              "outline": [c["geometry"]["coordinates"]]} if c["geometry"]["type"] == "Polygon" else
                             {"geo_code": c["properties"]["NUM_SECTEU"],
                                       "name": c["properties"]["NOM_ZF"],
                              "outline": c["geometry"]["coordinates"]}
                             for c in communes_geo])
    print(communes_outlines)
    print(communes_outlines[communes_outlines["geo_code"] == "29042"])

    return communes_outlines



if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)

    #zones_marseille = read_geojson("marseille", "epsg:2154", True)
    #print(zones_marseille.sort_values(by="id"))
    zones_lyon = read_geojson("lyon", "epsg:2154", True)
    print(zones_lyon.sort_values(by="id"))

    # to prevent from unuseful loading data
    security = True
    if not security:
        save_geo(zones_lyon)
