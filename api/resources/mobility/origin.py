import pandas as pd

from api.resources.common.log_stats import log_stats
from api.resources.mobility.utilities.get_travels_situation import get_travels_situation

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request


def get_origin(geo_codes):

    return {
        "origin": get_travels_situation(geo_codes),
    }


class Origin(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes

        log_stats("origin", geo_codes, None, None)
        message_request("origin", geo_codes)
        return get_origin(geo_codes)


if __name__ == '__main__':
    print("go")
    print(get_origin(["69123"]))
