import pandas as pd
import numpy as np

from api.resources.common.log_stats import log_stats
from api.resources.common.util_territory import get_neighbors
from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request


dataset_bnlc = {
    "endpoint": "offer/bnlc",
    "is_mesh_element": False,
    "meshes": None,
    "name_year": None,
    "years": None,
}

variables_table = ["id_lieu", "nom_lieu", "type", "insee", "Ylat", "Xlong",
                   "nbre_pl", "nbre_pmr", "date_maj", "saved_on"]
variables = ["id", "name", "type", "geo_code", "lat", "lon",
             "nbre_pl", "nbre_pmr", "date_maj", "saved_on"]


def get_bnlc(geo_codes):
    influence_geocodes = get_neighbors(geo_codes)
    all_geocodes = geo_codes + influence_geocodes

    result = db_request(
        """ SELECT """ + ", ".join([v for v in variables_table]) + """
            FROM transportdatagouv_bnlc
            WHERE insee IN :geo_codes 
        """,
        {
            "geo_codes": all_geocodes
        }
    )

    bnlc = pd.DataFrame(result, columns=variables)
    bnlc["date_maj"] = bnlc["date_maj"].astype(str)
    bnlc = bnlc.replace({np.nan: None})

    result = db_request(
        """ SELECT saved_on
            FROM transportdatagouv_bnlc
            LIMIT 1
        """, {})
    saved_on = result.scalar()

    source_data = saved_on.strftime("%m/%Y").title()
    bnlc.drop(columns=["saved_on"], inplace=True)

    return {
        "elements": {
            "bnlc": {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {
                        "coordinates": [lon, lat],
                        "geo_code": geo_code,
                        "name": name,
                        "type": type,
                        "nbre_pl": nbre_pl,
                        "nbre_pmr": nbre_pmr,
                        "date_maj": date_maj,
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    }
                } for lat, lon, geo_code, name, type, nbre_pl, nbre_pmr, date_maj in zip(
                    bnlc["lat"],
                    bnlc["lon"],
                    bnlc["geo_code"],
                    bnlc["name"],
                    bnlc["type"],
                    bnlc["nbre_pl"],
                    bnlc["nbre_pmr"],
                    bnlc["date_maj"],
                )]
            }
        },
        "sources": [{
            "label": f"Base nationale consolidée des lieux de covoiturage (TransportDataGouv {source_data})",
            "link": "https://transport.data.gouv.fr/datasets/base-nationale-des-lieux-de-covoiturage"
        }],
        "is_mesh_element": False,
    }


class BNLC(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes

        log_stats("bnlc", geo_codes, None, None)
        message_request("bnlc", geo_codes)
        return get_bnlc(geo_codes)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)
    print(get_bnlc(["57491"]))

