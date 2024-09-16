import pandas as pd
from data_manager.sncf.source import SOURCE_RAILWAYS_STATIONS

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_train_stations(geo_codes):
    result = db_request(
        """ SELECT name, lat, lon
            FROM sncf_stations
            WHERE geo_code IN :geo_codes
            AND year_data = :year_data
        """,
        {
            "geo_codes": geo_codes,
            "year_data": SOURCE_RAILWAYS_STATIONS
        }
    )

    train_stations = pd.DataFrame(result, columns=["name", "lat", "lon"])
    train_stations.dropna(inplace=True)
    train_stations["name"] = "Gare SNCF - " + train_stations["name"]
    train_stations["coords"] = [[lat, lon] for lat, lon in zip(train_stations["lat"], train_stations["lon"])]
    train_stations.drop(columns=["lat", "lon"], inplace=True)

    return {
        "train_stations": train_stations.to_dict(orient="list")
    }


class TrainStations(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("train_stations", geo_codes)
        return get_train_stations(geo_codes)

