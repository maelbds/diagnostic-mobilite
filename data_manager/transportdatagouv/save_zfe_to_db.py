import json
import pandas as pd
import numpy as np

from shapely.geometry import shape, GeometryCollection
from shapely import wkb

from data_manager.database_connection.sql_connect import mariadb_connection


def read_geojson():
    with open("data/zfe/aires_20221103.geojson", encoding="UTF-8") as data:
        geo = json.load(data)
    return geo


def get_zfe_from_geojson(geo):
    # geometry to wkb
    def geojson_to_wkb_geometry_collection(geojson):
        geom_coll = GeometryCollection([shape(geojson["geometry"])])
        geom_wkb = wkb.dumps(geom_coll)
        return geom_wkb

    def handle_feature(geojson_feature):
        properties = geojson_feature["properties"]
        properties["geometry"] = geojson_to_wkb_geometry_collection(geojson_feature)
        properties.pop("geo_point_2d", None)
        properties_df = pd.DataFrame(properties, index=[0])
        return properties_df

    features_df = [handle_feature(g) for g in geo["features"]]
    zfe = pd.concat(features_df, ignore_index=True)

    # variables https://github.com/etalab/schema-zfe/blob/master/schema.json
    zfe = zfe[["id", "date_debut", "date_fin",
               "vp_critair", "vp_horaires",
               "vul_critair", "vul_horaires",
               "pl_critair", "pl_horaires",
               "autobus_autocars_critair", "autobus_autocars_horaires",
               "deux_rm_critair", "deux_rm_horaires",
               "geometry"]]

    zfe["siren"] = [id.split("-")[0] for id in zfe["id"]]

    zfe = zfe.replace({np.nan: None})
    return zfe


def save_data_to_db(data, source):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ", SOURCE)"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ",?)"

    def request(cur, cols):
        cur.execute("""INSERT INTO transportdatagouv_zfe """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)+[source]) for index, row in data.iterrows()]

    conn.commit()
    conn.close()
    print("done")


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)

    geo = read_geojson()
    zfe = get_zfe_from_geojson(geo)
    print(zfe)

    security = True
    if not security:
        source = "ZFE_20221103"
        save_data_to_db(zfe, source)

