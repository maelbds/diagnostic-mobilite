import json
import pandas as pd
import numpy as np

from shapely.geometry import shape, GeometryCollection
from shapely import wkb

from data_manager.database_connection.sql_connect import mariadb_connection


def read_geojson():
    with open("data/amenagements-cyclables/bicycle_parking_geojson/data.geojson", encoding="UTF-8") as data:
        geo = json.load(data)
    return geo


def get_cycle_parkings_from_geojson(geo):
    # geometry to wkb
    def geojson_to_wkb_geometry_collection(geojson):
        geom_coll = GeometryCollection([shape(geojson["geometry"])])
        geom_wkb = wkb.dumps(geom_coll)
        return geom_wkb

    def handle_feature(geojson_feature):
        properties = geojson_feature["properties"]
        properties["lat"] = properties["coordonneesxy"][1]
        properties["lon"] = properties["coordonneesxy"][0]
        properties.pop("coordonneesxy")
        #properties["geometry"] = geojson_to_wkb_geometry_collection(geojson_feature)
        properties_df = pd.DataFrame(properties, index=[0])
        return properties_df

    features_df = [handle_feature(g) for g in geo["features"]]
    cycle_parkings = pd.concat(features_df, ignore_index=True)
    cycle_parkings["capacite"] = pd.to_numeric(cycle_parkings["capacite"], errors="coerce", downcast="integer")

    print(cycle_parkings)
    # variables https://schema.data.gouv.fr/schemas/etalab/schema-amenagements-cyclables/0.3.3/schema_amenagements_cyclables.json
    cycle_parkings = cycle_parkings[["id_local", "id_osm", "code_com", "lon", "lat",
                                     "capacite", "acces", "gestionnaire", "date_maj"]]

    cycle_parkings = cycle_parkings.replace({np.nan: None})
    return cycle_parkings


def save_data_to_db(data, source):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ", source)"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ", ?)"

    def request(cur, cols):
        cur.execute("""INSERT INTO transportdatagouv_cycle_parkings """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values) + [source]) for index, row in data.iterrows()]

    conn.commit()
    conn.close()
    print("done")


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)

    geo = read_geojson()
    print(geo["features"][0])
    cycle_paths = get_cycle_parkings_from_geojson(geo)
    print(cycle_paths)

    security = True
    if not security:
        source = "OSM_20230213" #OSM_20230201
        save_data_to_db(cycle_paths, source)

