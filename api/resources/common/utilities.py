from shapely import wkb


def wkb_to_geojson(wkb_geom):
    geom_collection = wkb.loads(wkb_geom)
    geom = geom_collection.__geo_interface__
    return geom
