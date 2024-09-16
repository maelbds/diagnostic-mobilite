import pandas as pd

from api.resources.common.log_stats import log_stats
from api.resources.mobility.utilities.get_travels_sources import get_travels_sources
from api.resources.mobility.utilities.get_travels import get_travels

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request
from api.resources.mobility.utilities.significance_threshold import SIGNIFICANCE_THRESHOLD


def get_reasons(geo_codes):
    travels = get_travels(geo_codes)

    if len(travels) == 0:
        return {
            "reasons": None,
            "sources": []
        }

    reasons_nb = travels.groupby("reason_name_fr")["w_trav"].sum().round()
    reasons_dist = travels.groupby("reason_name_fr") \
        .apply(lambda df: (df["w_trav"] * df["distance"]).sum().round())
    reasons_significance = travels.groupby("reason_name_fr") \
        .apply(lambda df: df["id_ind"].drop_duplicates().count())

    reasons = pd.DataFrame({
        "number": reasons_nb,
        "distance": reasons_dist,
        "id": reasons_significance
    }).reset_index()

    mask_significance = reasons["id"] < SIGNIFICANCE_THRESHOLD
    reasons.loc[mask_significance, "reason_name_fr"] = "imprécis"

    reasons = reasons.groupby("reason_name_fr").sum()

    return {
        "reasons": reasons.to_dict(),
        "references": {
            "france": {}
        },
        "sources": get_travels_sources(geo_codes),
    }


class Reasons(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes

        log_stats("modes", geo_codes, None, None)
        message_request("modes", geo_codes)
        return get_reasons(geo_codes)


if __name__ == '__main__':
    print(get_reasons(["691233"]))

