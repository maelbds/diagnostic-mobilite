"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import os

import pandas as pd
import shapefile
import numpy as np

from shapely.geometry import shape, Polygon, MultiPolygon, GeometryCollection
from shapely import wkb

from data_manager.db_functions import load_database

from data_manager.utilities import load_file_ign


def download_files():
    # reference : "https://geoservices.ign.fr/adminexpress"

    files = [{
        "name": "ADMIN-EXPRESS-COG édition 2021 France entière",
        "url": "https://wxs.ign.fr/x02uy2aiwjo9bm8ce5plwqmr/telechargement/prepackage/ADMINEXPRESS-COG_SHP_WGS84G_PACK_2021-05-19$ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19/file/ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19.7z",
        "dir": "data/2021",
        "zip_name": "ign_admin_express_2021.zip",
        "file_name": "ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19/ADMIN-EXPRESS-COG/1_DONNEES_LIVRAISON_2021-05-19/ADECOG_3-0_SHP_WGS84G_FRA/EPCI.shp",
    }]

    [load_file_ign(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"]) for f in files]


def read_shp_outlines():
    # geometry to wkb
    def geojson_to_wkb_geometry_collection(geojson):
        geom_coll = GeometryCollection([shape(geojson["geometry"])])
        geom_wkb = wkb.dumps(geom_coll)
        return geom_wkb

    print("Reading shp EPCI")
    sf = shapefile.Reader(
        "data/2021/ADMIN-EXPRESS-COG_3-0__SHP_WGS84G_FRA_2021-05-19/ADMIN-EXPRESS-COG/1_DONNEES_LIVRAISON_2021-05-19/ADECOG_3-0_SHP_WGS84G_FRA/EPCI")
    shapes = sf.shapeRecords()
    """
    epci_geo = {"type": "FeatureCollection", "features": [s.__geo_interface__ for s in shapes]}
    with open('total_epci_geo.json', 'w') as outfile:
        json.dump(epci_geo, outfile)

    # geojson shapes
    outlines = [s.__geo_interface__ for s in shapes]
    light_outlines = simplify_outline(outlines, 0.003)
    """

    epcis = pd.DataFrame([{
        "epci_siren": s.__geo_interface__["properties"]["CODE_SIREN"],
        "outline": geojson_to_wkb_geometry_collection(s.__geo_interface__),
        "year_data": "2021",
        "year_cog": "2021"
    } for s in shapes])
    epcis = epcis.replace({np.nan: None})
    print(epcis)

    """
    epci = pd.DataFrame({"epci_siren": [o["properties"]["CODE_SIREN"] for o in outlines]})
    epci["outline"] = [geojson_to_wkb_geometry_collection(o) for o in outlines]
    epci["outline_light"] = [geojson_to_wkb_geometry_collection(o) for o in light_outlines]
    epci["source"] = "IGN 2022"
    print(epci)"""

    return epcis


def load_epci_outline(pool, table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data = read_shp_outlines()

    cols_table = {
        "epci_siren": "VARCHAR(50) NOT NULL",
        "outline": "GEOMETRYCOLLECTION NULL DEFAULT NULL",
        "year_data": "VARCHAR(12) NULL DEFAULT NULL",
        "year_cog": "VARCHAR(12) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (epci_siren, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    epci_outlines = read_shp_outlines()

    # to prevent from unuseful loading data
    security = True
    if not security:
        load_epci_outline(None, "ign_epci_outline")
