import pandas as pd
import os
import json
from shapely import geometry, wkb


def read_emd_geo_geojson(emd_id, encoding="UTF-8"):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    with open(f"data/{emd_id}/geo/zones_fines.geojson", encoding=encoding) as data:
        geo = json.load(data)

    geo = pd.DataFrame({
        "id": f["properties"]["NUM_ZF_201"].replace(" ", ""),
        "name": f["properties"]["NOM_ZF"],
        "geometry": f["geometry"],
    } for f in geo["features"])

    dict_geocode = pd.read_csv(f"data/{emd_id}/geo/correspondances_zones_geocodes.csv", sep=";", dtype=str)
    geo = pd.merge(geo, dict_geocode, left_on="id", right_on="id_zone", how="left").drop(columns=["id_zone"])

    geo["emd_id"] = emd_id

    # geometry to wkb
    def geojson_to_wkb_geometry_collection(geo):
        geom = geometry.shape(geo)
        geom_coll = geometry.GeometryCollection([geom])
        geom_wkb = wkb.dumps(geom_coll)
        return geom_wkb

    geo["geometry"] = geo["geometry"].apply(lambda geo: geojson_to_wkb_geometry_collection(geo))

    return geo


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)

    read_emd_geo_geojson("montpellier")

