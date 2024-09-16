import pandas as pd

from api.resources.common.log_stats import log_stats
from api.resources.mobility.utilities.get_travels_sources import get_travels_sources
from api.resources.mobility.utilities.get_travels import get_travels

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request
from api.resources.mobility.utilities.significance_threshold import SIGNIFICANCE_THRESHOLD


def get_modes(geo_codes):
    travels = get_travels(geo_codes)

    if len(travels) == 0:
        return {
            "modes": None,
            "sources": []
        }

    modes_nb = travels.groupby("mode_name_fr")["w_trav"].sum().round()
    modes_dist = travels.groupby("mode_name_fr") \
        .apply(lambda df: (df["w_trav"] * df["distance"]).sum().round())
    modes_significance = travels.groupby("mode_name_fr") \
        .apply(lambda df: df["id_ind"].drop_duplicates().count())

    modes = pd.DataFrame({
        "number": modes_nb,
        "distance": modes_dist,
        "id": modes_significance
    }).reset_index()

    mask_significance = modes["id"] < SIGNIFICANCE_THRESHOLD
    modes.loc[mask_significance, "mode_name_fr"] = "imprécis"

    modes = modes.groupby("mode_name_fr").sum()

    return {
        "modes": modes.to_dict(),
        "references": {
            "france": {}
        },
        "sources": get_travels_sources(geo_codes),
    }


class Modes(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes

        log_stats("modes", geo_codes, None, None)
        message_request("modes", geo_codes)
        return get_modes(geo_codes)


if __name__ == '__main__':
    print("go")
    print(get_modes(["34172"]))
