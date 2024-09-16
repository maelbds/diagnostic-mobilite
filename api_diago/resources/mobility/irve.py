import pandas as pd
import numpy as np

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_irve(geo_codes):
    result = db_request(
        """ SELECT id, id_station_itinerance, nom_station, code_insee_commune, lat, lon, 
                   nbre_pdc, puissance_nominale, date_maj
            FROM transportdatagouv_irve 
            WHERE code_insee_commune IN :geo_codes
        """,
        {
            "geo_codes": geo_codes
        }
    )

    irve = pd.DataFrame(result, columns=["id", "id_station", "nom_station", "geo_code", "lat", "lon",
                                         "nbre_pdc", "puissance_nominale", "date_maj"])

    irve["nbre_pdc"] = irve["nbre_pdc"].replace({np.nan: None})
    irve["date_maj"] = irve["date_maj"].astype(str)

    irve.drop_duplicates(subset=["nom_station", "geo_code", "lat", "lon", "nbre_pdc", "puissance_nominale", "date_maj"],
                         inplace=True)

    return {
            "irve": irve.to_dict(orient="list")
        }


class IRVE(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("irve", geo_codes)
        return get_irve(geo_codes)

