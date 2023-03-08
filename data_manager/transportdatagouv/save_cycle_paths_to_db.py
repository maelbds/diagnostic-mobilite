import json
import pandas as pd
import numpy as np

from shapely.geometry import shape, GeometryCollection
from shapely import wkb

from data_manager.database_connection.sql_connect import mariadb_connection


def read_geojson():
    with open("data/amenagements-cyclables/france-20230201.geojson", encoding="UTF-8") as data:
        geo = json.load(data)
    return geo

def get_cycle_paths_from_geojson(geo, batch_i):
    # geometry to wkb
    def geojson_to_wkb_geometry_collection(geojson):
        geom_coll = GeometryCollection([shape(geojson["geometry"])])
        geom_wkb = wkb.dumps(geom_coll)
        return geom_wkb

    def handle_feature(geojson_feature):
        properties = geojson_feature["properties"]
        properties["geometry"] = geojson_to_wkb_geometry_collection(geojson_feature)
        properties_df = pd.DataFrame(properties, index=[0])
        return properties_df

    features_df = [handle_feature(g) for g in geo["features"][batch_i*10000:(batch_i+1)*10000]]
    cycle_paths = pd.concat(features_df, ignore_index=True)

    # variables https://schema.data.gouv.fr/schemas/etalab/schema-amenagements-cyclables/0.3.3/schema_amenagements_cyclables.json
    cycle_paths = cycle_paths[["id_local", "id_osm", "code_com_d", "code_com_g", "ame_d", "ame_g",
                               "sens_g", "sens_d", "trafic_vit", "date_maj", "geometry"]]

    cycle_paths = cycle_paths.replace({np.nan: None})
    return cycle_paths


def save_data_to_db(data, source):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ", SOURCE)"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + "," + source + ")"

    def request(cur, cols):
        cur.execute("""INSERT INTO transportdatagouv_cycle_paths """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

    conn.commit()
    conn.close()
    print("done")


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)

    security = True
    if security:
        geo = read_geojson()
        source = "TO_COMPLETE" #OSM_20230201
        for i in range(100000):
            print(f"BATCH {i}")
            cycle_paths = get_cycle_paths_from_geojson(geo, i)
            print(cycle_paths)
            save_data_to_db(cycle_paths, source)

