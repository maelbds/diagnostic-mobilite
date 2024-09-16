import pandas as pd
import geopandas as gpd
import json
from shapely import wkb

from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.log_stats import log_stats
from api.resources.common.schema_request import context_get_request


dataset_zfe = {
    "endpoint": "offer/zfe",
    "is_mesh_element": False,
    "meshes": None,
    "name_year": None,
    "years": None,
}

variables = ["id", "date_debut", "vp_critair", "vp_horaires", "geometry", "saved_on"]


def get_zfe():
    result = db_request(
        """ SELECT """ + ", ".join([v for v in variables]) + """
            FROM transportdatagouv_zfe
        """,
        {}
    )

    zfe = pd.DataFrame(result, columns=variables)
    zfe["geometry"] = [wkb.loads(r) for r in zfe["geometry"]]

    source_data = zfe["saved_on"].iloc[0].strftime("%m/%Y").title()
    zfe.drop(columns=["saved_on"], inplace=True)
    zfe["date_debut"] = zfe["date_debut"].astype(str)

    return {
        "elements": {
            "zfe": json.loads(gpd.GeoDataFrame(zfe).to_json(drop_id=True))
        },
        "sources": [{
            "label": f"Base Nationale des Zones à Faibles Émissions (TransportDataGouv {source_data})",
            "link": "https://transport.data.gouv.fr/datasets/base-nationale-consolidee-des-zones-a-faibles-emissions"
        }],
        "is_mesh_element": False,
    }


class ZFE(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("zfe", geo_codes)
        log_stats("zfe", geo_codes, None, None)
        return get_zfe()


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)
    print(get_zfe())

