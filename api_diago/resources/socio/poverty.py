import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP, SOURCE_FILOSOFI

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_poverty(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT pov.CODGEO, pov.poverty_rate_all, pov.poverty_rate_75p, pov.poverty_rate_30m
                FROM observatoire_insee_filosofi_pauvrete_com AS pov
                WHERE pov.CODGEO IN :geo_codes
                AND pov.year_data = :year_pov
            """,
            {
                "geo_codes": geo_codes,
                "year_pov": SOURCE_FILOSOFI,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "poverty_rate_all", "poverty_rate_75p", "poverty_rate_30m"])
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: None})

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT pov.CODGEO, pov.poverty_rate_all, pov.poverty_rate_75p, pov.poverty_rate_30m
                FROM observatoire_insee_filosofi_pauvrete_epci AS pov
                WHERE pov.CODGEO IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes 
                    AND epci2.year_data = :year_epci
                  ) 
                AND pov.year_data = :year_pov
            """,
            {
                "geo_codes": geo_codes,
                "year_pov": SOURCE_FILOSOFI,
                "year_epci": SOURCE_EPCI,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "poverty_rate_all", "poverty_rate_75p", "poverty_rate_30m"])
        data = data.replace({np.nan: None})
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class Poverty(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("poverty", geo_codes)
        return get_poverty(geo_codes, mesh)
