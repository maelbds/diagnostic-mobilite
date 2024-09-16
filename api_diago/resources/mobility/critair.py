import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.rsvero.source import SOURCE_CAR_FLEET

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_critair(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT geo_code, critair1, critair2, critair3, critair4, critair5, electrique, non_classe 
                FROM rsvero_critair 
                WHERE geo_code IN :geo_codes
                AND source = :source
            """,
            {
                "geo_codes": geo_codes,
                "source": SOURCE_CAR_FLEET,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code",
                                             "critair1", "critair2", "critair3", "critair4", "critair5",
                                             "electrique", "non_classe"])
        data["total"] = data.sum(axis=1)
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: None})

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT epci.EPCI, critair1, critair2, critair3, critair4, critair5, electrique, non_classe 
                FROM rsvero_critair 
                JOIN insee_epci_communes AS epci ON geo_code = epci.CODGEO
                WHERE epci.EPCI IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND source = :source
                AND epci.year_data = :year_epci
            """,
            {
                "geo_codes": geo_codes,
                "source": SOURCE_CAR_FLEET,
                "year_epci": SOURCE_EPCI,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code",
                                             "critair1", "critair2", "critair3", "critair4", "critair5",
                                             "electrique", "non_classe"])
        data["total"] = data.sum(axis=1)
        data = data.groupby(by="geo_code", as_index=False).sum()
        data = data.replace({np.nan: None})
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class Critair(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("critair", geo_codes)
        return get_critair(geo_codes, mesh)

