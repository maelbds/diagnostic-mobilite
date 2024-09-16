import pandas as pd

from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.log_stats import log_stats
from api.resources.common.schema_request import context_get_request


dataset_train_stations = {
    "endpoint": "offer/train_stations",
    "is_mesh_element": False,
    "meshes": None,
    "name_year": "SNCF",
    "years": None,
}


def get_train_stations(geo_codes):
    result = db_request(
        """ SELECT name, lat, lon
            FROM sncf_stations
            WHERE geo_code IN :geo_codes
        """,
        {
            "geo_codes": geo_codes
        }
    )

    train_stations = pd.DataFrame(result, columns=["name", "lat", "lon"])
    train_stations.dropna(inplace=True)

    stations = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {
                "name": name.title(),
            },
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            }
        } for name, lat, lon in zip(
            train_stations["name"],
            train_stations["lat"],
            train_stations["lon"],
        )]
    }

    return {
        "elements": {
            "train_stations": stations
        },
        "sources": {
            "label": "Gares de voyageurs (SNCF 2024)",
            "link": "https://ressources.data.sncf.com/explore/dataset/referentiel-gares-voyageurs/table/"
        },
        "is_mesh_element": False
    }


class TrainStations(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes

        log_stats("train stations", geo_codes, None, None)
        message_request("train_stations", geo_codes)
        return get_train_stations(geo_codes)
