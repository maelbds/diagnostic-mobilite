import pandas as pd

from api.resources.common.log_stats import log_stats
from api.resources.mobility.utilities.get_travels_sources import get_travels_sources
from api.resources.mobility.utilities.get_travels import get_travels

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request
from api.resources.mobility.utilities.significance_threshold import SIGNIFICANCE_THRESHOLD


def get_key_figures(geo_codes):
    travels = get_travels(geo_codes)
    significance = travels["id_ind"].drop_duplicates().count()

    if len(travels) == 0 or significance < SIGNIFICANCE_THRESHOLD * 2:
        return {
            "total_nb": "--",
            "total_dist": "--",
            "total_dist_pers": "--",
            "total_nb_pers": "--",
            "sources": []
        }

    total_nb = travels["w_trav"].sum().round()
    total_dist = (travels["w_trav"] * travels["distance"]).sum().round()

    mobile_persons = travels[["id_ind", "w_ind"]].drop_duplicates(subset=["id_ind"])["w_ind"].sum()
    total_nb_pers = round(total_nb / mobile_persons, 2)
    total_dist_pers = round(total_dist / mobile_persons)

    return {
        "total_nb": total_nb,
        "total_dist": total_dist,
        "total_dist_pers": total_dist_pers,
        "total_nb_pers": total_nb_pers,
        "references": {
            "france": {}
        },
        "sources": get_travels_sources(geo_codes),
    }


class KeyFiguresMobility(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes

        log_stats("key_figures", geo_codes, None, None)
        message_request("key_figures", geo_codes)
        return get_key_figures(geo_codes)


if __name__ == '__main__':
    print("go")
    print(get_key_figures(["79270"]))
