import pandas as pd
import numpy as np

from api.resources.common.cog import COG
from api.resources.common.log_stats import log_stats
from api.resources.common.util_territory import get_neighbors
from data_manager.sources.sources import get_years_for_source, get_label_link_for_source_year

from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request

source_label = "insee_bpe"

dataset_health = {
    "endpoint": "territory/health",
    "is_mesh_element": False,
    "meshes": None,
    "name_year": "INSEE BPE",
    "years": get_years_for_source(source_label),
}


def get_bpe_health(geo_codes, year):
    result = db_request(
        """SELECT insee_bpe.id, p.CODGEO_DES,
                    types.name, insee_bpe_types.name,
                    insee_bpe.lat, insee_bpe.lon 
            FROM insee_bpe 
            JOIN insee_passage_cog AS p ON insee_bpe.geo_code = p.CODGEO_INI

            JOIN insee_bpe_types ON insee_bpe.id_type = insee_bpe_types.id
            JOIN types ON insee_bpe_types.id_type = types.id
            JOIN categories ON types.id_category = categories.id
            JOIN reasons ON categories.id_reason = reasons.id

            WHERE p.CODGEO_DES IN :geo_codes
            AND insee_bpe.year_data = :year_data
            AND insee_bpe_types.to_keep = 1 
            AND categories.id != 1
            AND (categories.id = 10 OR categories.id = 9)
            AND p.year_cog = :cog
        """,
        {
            "geo_codes": geo_codes,
            "year_data": year,
            "cog": COG
        }
    )
    bpe_places = pd.DataFrame(result, columns=["id", "geo_code",
                                               "type", "name",
                                               "lat", "lon"])
    return bpe_places


def format_places(places):
    places.dropna(subset=["lat", "lon"], inplace=True)
    places["coords_geo"] = [[lon, lat] for lat, lon in zip(places["lat"], places["lon"])]
    places.drop(columns=["lat", "lon"], inplace=True)
    places["name"] = [p.title() for p in places["name"]]
    return places


def get_health(geo_codes, year):
    sources = [get_label_link_for_source_year(name, year) for name in [source_label]]

    influence_geocodes = get_neighbors(geo_codes)
    all_geocodes = geo_codes + influence_geocodes

    places = get_bpe_health(all_geocodes, year)
    places = format_places(places)

    places = places.replace({np.nan: None})

    return {
        "elements": {
            "health": {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {
                        "coordinates": coords,
                        "geo_code": geo_code,
                        "name": name,
                        "type": type,
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": coords
                    }
                } for coords, name, type, geo_code in zip(
                    places["coords_geo"],
                    places["name"],
                    places["type"],
                    places["geo_code"],
                )]
            }},
        # "legend": legend.to_dict(orient="list"),
        "sources": sources,
        "is_mesh_element": False
    }


class Health(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes
        year = perimeter.year

        log_stats("health", geo_codes, None, year)
        message_request("health", geo_codes)
        return get_health(geo_codes, year)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    print(get_health(["79191"], "2021"))
