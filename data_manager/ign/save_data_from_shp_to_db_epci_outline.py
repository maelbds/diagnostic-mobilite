"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import os
import shutil

import pandas as pd
import shapefile
import numpy as np

from shapely.geometry import shape, Polygon, MultiPolygon, GeometryCollection
from shapely import wkb

from data_manager.db_functions import load_database
from data_manager.sources.sources import missing_sources_for_table, save_source

from data_manager.utilities import load_file_ign


def download_file(id, name, table_name, label, link, reference, year_data, year_cog):
    f = {
        "name": id,
        "url": link,
        "dir": f"data/{year_cog}/{id}",
        "zip_name": f"{id}.7z",
        "file_name": "EPCI.shp",
    }
    filter_func = lambda f: os.path.basename(f).split(".")[0] == "EPCI"

    return load_file_ign(f["name"], f["url"], f["dir"], f["zip_name"], f["file_name"], filter_func)


def get_epci_outline(file_name, id, name, table_name, label, link, reference, year_data, year_cog):
    # geometry to wkb
    def geojson_to_wkb_geometry_collection(geojson):
        geom_coll = GeometryCollection([shape(geojson["geometry"])])
        geom_wkb = wkb.dumps(geom_coll)
        return geom_wkb

    print("Reading shp EPCI")
    sf = shapefile.Reader(file_name.replace(".shp", ""))
    shapes = sf.shapeRecords()

    epcis = pd.DataFrame([{
        "epci_siren": s.__geo_interface__["properties"]["CODE_SIREN"],
        "outline": geojson_to_wkb_geometry_collection(s.__geo_interface__),

        "year_cog": year_cog
    } for s in shapes])
    epcis = epcis.replace({np.nan: None})
    print(epcis)

    return epcis


def load_epci_outline(pool):
    table_name = "ign_epci_outline"
    cols_table = {
        "epci_siren": "VARCHAR(50) NOT NULL",
        "outline": "GEOMETRYCOLLECTION NULL DEFAULT NULL",

        "year_cog": "VARCHAR(12) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (epci_siren, year_cog) USING BTREE"

    ms = missing_sources_for_table(table_name)
    for missing_source in zip(ms["id"], ms["name"], ms["table_name"], ms["label"], ms["link"], ms["reference"], ms["year_data"], ms["year_cog"]):
        id, name, table_name, label, link, reference, year_data, year_cog = missing_source

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        file_name = download_file(*missing_source)
        data = get_epci_outline(file_name, *missing_source)

        load_database(pool, table_name, data, cols_table, keys)

        shutil.rmtree(f"data/{year_cog}/{id}")
        save_source(pool, *missing_source)


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    # to prevent from unuseful loading data
    security = False
    if not security:
        load_epci_outline(None)
