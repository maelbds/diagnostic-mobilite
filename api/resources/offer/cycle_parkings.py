import pandas as pd
import numpy as np

from api.resources.common.log_stats import log_stats
from api.resources.common.util_territory import get_neighbors
from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request


dataset_cycle_parkings = {
    "endpoint": "offer/cycle_parkings",
    "is_mesh_element": False,
    "meshes": None,
    "name_year": None,
    "years": None,
}

variables = ["id", "code_com", "lat", "lon", "capacite", "gestionnaire", "date_maj", "saved_on"]


def get_cycle_parkings(geo_codes):
    influence_geocodes = get_neighbors(geo_codes)
    all_geocodes = geo_codes + influence_geocodes

    result = db_request(
        """ SELECT """ + ", ".join([v for v in variables]) + """
            FROM transportdatagouv_cycle_parkings
            WHERE code_com IN :geo_codes 
        """,
        {
            "geo_codes": all_geocodes
        }
    )

    cycle_parkings = pd.DataFrame(result, columns=variables)
    cycle_parkings["date_maj"] = cycle_parkings["date_maj"].astype(str)
    cycle_parkings = cycle_parkings.replace({np.nan: None})

    result = db_request(
        """ SELECT saved_on
            FROM transportdatagouv_cycle_parkings
            LIMIT 1
        """, {})
    saved_on = result.scalar()

    source_data = saved_on.strftime("%m/%Y").title()
    cycle_parkings.drop(columns=["saved_on"], inplace=True)

    return {
        "elements": {
            "cycle_parkings": {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {
                        "coordinates": [lon, lat],
                        "geo_code": code_com,
                        "capacite": capacite,
                        "gestionnaire": gestionnaire,
                        "date_maj": date_maj,
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    }
                } for lat, lon, code_com, capacite, date_maj, gestionnaire in zip(
                    cycle_parkings["lat"],
                    cycle_parkings["lon"],
                    cycle_parkings["code_com"],
                    cycle_parkings["capacite"],
                    cycle_parkings["date_maj"],
                    cycle_parkings["gestionnaire"],
                )]
            }
        },
        "sources": [{
            "label": f"Base Nationale du Stationnement Cyclable (OpenStreetMap {source_data})",
            "link": "https://transport.data.gouv.fr/datasets/stationnements-cyclables-issus-dopenstreetmap"
        }],
        "is_mesh_element": False,
    }


class CycleParkings(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes

        log_stats("cycle parkings", geo_codes, None, None)
        message_request("cycle parkings", geo_codes)
        return get_cycle_parkings(geo_codes)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)
    print(get_cycle_parkings(["79048"]))

