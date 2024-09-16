import os
import json
import shutil

import pandas as pd
import numpy as np
import shapefile
from shapely import wkb

from shapely.geometry import shape, GeometryCollection

from data_manager.utilities import load_file_ign
from api.resources.common.db_request import db_request


def download_file(id, link, year_cog):
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_cog}/{id}",
        "zip_name": f"{id}.7z",
        "file_name": "COMMUNE.shp",
    }
    filter_func = lambda f: os.path.basename(f).split(".")[0] == "COMMUNE"

    return load_file_ign(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"], filter_func)


"""
First with https://mapshaper.org/ load downloaded COMMUNE shapefile
simplify topography with (in the console) : 
-simplify variable percentage='INSEE_COM == "50353" ? "100%" : "7%"' keep-shapes
export topojson to COMMUNE.json

Then create light version from previously exported topojson file :
-simplify variable percentage='INSEE_COM == "50353" ? "100%" : "30%"' keep-shapes
-proj webmercator \
-affine where="INSEE_COM.indexOf('971')==0" shift=6355000,3330000 scale=1.5 \
-affine where="INSEE_COM.indexOf('972')==0" shift=6480000,3505000 scale=1.5 \
-affine where="INSEE_COM.indexOf('973')==0" shift=5760000,4720000 scale=0.35 \
-affine where="INSEE_COM.indexOf('974')==0" shift=-6170000,7560000 scale=1.5 \
-affine where="INSEE_COM.indexOf('976')==0" shift=-4885000,6590000 scale=1.5 
export topojson to COMMUNE_selection.json

Finally use process_topojson_attributes function to standardize these to topojson files 
"""


def get_communes_attr():
    result = db_request(
        """ SELECT COM, LIBELLE, DEP, REG, centroid_lat, centroid_lon, chflieu_lat, chflieu_lon
            FROM insee_cog_communes AS cog
            LEFT JOIN ign_commune_center AS ign ON cog.COM = ign.geo_code
            WHERE cog.year_cog = :year_cog AND ign.year_cog = :year_cog
        """,
        {
            "year_cog": "2023"
        }
    )

    communes = pd.DataFrame(result, columns=["geo_code", "libgeo", "dep", "reg",
                                             "centroid_lat", "centroid_lon", "chflieu_lat", "chflieu_lon"])
    mask_no_chflieu = communes["chflieu_lat"].isna() | communes["chflieu_lon"].isna()
    communes.loc[mask_no_chflieu, "chflieu_lat"] = communes.loc[mask_no_chflieu, "centroid_lat"]
    communes.loc[mask_no_chflieu, "chflieu_lon"] = communes.loc[mask_no_chflieu, "centroid_lon"]

    communes = communes.drop(columns=["centroid_lat", "centroid_lon"])
    communes = communes.set_index("geo_code")

    print(communes)
    return communes


def process_topojson_attributes():
    with open('data/COMMUNE.json') as f:
        topo = json.load(f)

    communes_cog = get_communes_attr()

    def set_attributes(geometry):
        codgeo = geometry["properties"]["INSEE_COM"]
        attr = communes_cog.loc[codgeo]
        return {
            "type": geometry["type"],
            "arcs": geometry["arcs"],
            "properties": {
                "codgeo": codgeo,
                "libgeo": attr["libgeo"], # needed for main version, but not needed for light version
                #"dep": attr["dep"],
                #"reg": attr["reg"],
                #"cl_lat": attr["chflieu_lat"],
                #"cl_lon": attr["chflieu_lon"],
            },
        }

    n_topo = {
        "type": "Topology",
        "transform": topo["transform"],
        "arcs": topo["arcs"],
        "objects": {
            "com": {
                "type": "GeometryCollection",
                "geometries": [set_attributes(g) for g in topo["objects"]["COMMUNE"]["geometries"]],
            }
        }
    }

    with open('data/topo_com_with_attr.json', 'w') as f:
        json.dump(n_topo, f, separators=(',', ':'))


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    #download_file("IGN_CARTO_2023",
    #              "https://data.geopf.fr/telechargement/download/ADMIN-EXPRESS-COG-CARTO/ADMIN-EXPRESS-COG-CARTO_3-2__SHP_WGS84G_FRA_2023-05-03/ADMIN-EXPRESS-COG-CARTO_3-2__SHP_WGS84G_FRA_2023-05-03.7z",
    #              2023)

    process_topojson_attributes()

