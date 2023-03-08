import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely import wkb

import pyproj
from shapely.ops import transform

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.transportdatagouv.source import SOURCE_CYCLE_PATHS


def get_cycle_paths(pool, geo_codes):
    def wkb_to_geojson(wkb_geom):
        geom_collection = wkb.loads(wkb_geom)
        geom = geom_collection[0].__geo_interface__
        return geom

    conn = mariadb_connection(pool)
    cur = conn.cursor()

    def get_cycle_path_by_geo_code(geo_code):
        cur.execute("""SELECT id_local, id_osm, code_com_g, code_com_d, ame_d, ame_g, 
                                sens_d, sens_g, source, date_maj, geometry
                    FROM transportdatagouv_cycle_paths 
                    WHERE ((code_com_g = ? OR code_com_d = ?) AND source = ?)""", [geo_code, geo_code, SOURCE_CYCLE_PATHS])
        result = list(cur)

        cycle_paths = pd.DataFrame(result, columns=["id_local", "id_osm", "code_com_g", "code_com_d",
                                                    "ame_d", "ame_g", "sens_d", "sens_g",
                                                    "source", "date_maj", "geometry"])
        return cycle_paths

    all_cycle_paths = pd.concat([get_cycle_path_by_geo_code(g) for g in geo_codes])

    conn.close()

    all_cycle_paths["geometry_shape"] = [wkb.loads(r)[0] for r in all_cycle_paths["geometry"]]

    wgs84 = pyproj.CRS('EPSG:4326')
    lambert = pyproj.CRS('EPSG:2154')
    project = pyproj.Transformer.from_crs(wgs84, lambert, always_xy=True).transform

    all_cycle_paths["geometry_shape_lambert"] = [transform(project, shape) for shape in all_cycle_paths["geometry_shape"]]
    all_cycle_paths["length_segment"] = [shape.length for shape in all_cycle_paths["geometry_shape_lambert"]]
    all_cycle_paths["length_segment"] = all_cycle_paths["length_segment"].round(1)

    all_cycle_paths["coef_sens_g"] = [2 if s == "BIDIRECTIONNEL" else 1 for s in all_cycle_paths["sens_g"]]
    all_cycle_paths["coef_sens_d"] = [2 if s == "BIDIRECTIONNEL" else 1 for s in all_cycle_paths["sens_d"]]
    all_cycle_paths["coef_ame_g"] = [0 if ame == "AUCUN" else 1 for ame in all_cycle_paths["ame_g"]]
    all_cycle_paths["coef_ame_d"] = [0 if ame == "AUCUN" else 1 for ame in all_cycle_paths["ame_d"]]
    all_cycle_paths["coef_path"] = all_cycle_paths["coef_ame_d"] * all_cycle_paths["coef_sens_d"] + \
                                   all_cycle_paths["coef_ame_g"] * all_cycle_paths["coef_sens_g"]

    all_cycle_paths["length_path"] = all_cycle_paths["length_segment"] * all_cycle_paths["coef_path"]
    all_cycle_paths.drop(columns=["geometry_shape", "geometry_shape_lambert",
                                  "coef_sens_g", "coef_sens_d",
                                  "coef_ame_g", "coef_ame_d", "coef_path", "length_segment"], inplace=True)

    all_cycle_paths["geometry"] = [wkb_to_geojson(r) for r in all_cycle_paths["geometry"]]
    all_cycle_paths["date_maj"] = all_cycle_paths["date_maj"].astype(str)

    return all_cycle_paths


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)

    cycle_paths = get_cycle_paths(None, ["13201"])
    print(cycle_paths)
    print(cycle_paths.dtypes)
    print(cycle_paths[cycle_paths["sens_g"]!="UNIDIRECTIONNEL"])