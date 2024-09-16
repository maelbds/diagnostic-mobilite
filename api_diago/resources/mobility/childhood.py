import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_childhood(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT bpe.geo_code, bpe.id_type
                FROM insee_bpe AS bpe
                WHERE bpe.geo_code IN :geo_codes
                AND id_type = 'D502'
            """,
            {
                "geo_codes": geo_codes,
            }
        )
        data = pd.DataFrame(result, columns=["geo_code", "nurseries_nb"])
        data = data.groupby("geo_code", as_index=False).count()

        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: 0})

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT epci.EPCI, bpe.id_type
                FROM insee_bpe AS bpe
                JOIN insee_epci_communes AS epci ON bpe.geo_code = epci.CODGEO                     
                WHERE epci.EPCI IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND id_type = 'D502'
                AND epci.year_data = :year_epci
            """,
            {
                "geo_codes": geo_codes,
                "year_epci": SOURCE_EPCI,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "nurseries_nb"])
        data = data.groupby("geo_code", as_index=False).count()

        result = db_request(
            """ SELECT epci.EPCI
                FROM insee_epci_communes AS epci
                WHERE epci.CODGEO IN :geo_codes
                AND epci.year_data = :year_epci
            """,
            {
                "geo_codes": geo_codes,
                "year_epci": SOURCE_EPCI,
            }
        )
        geo_codes = pd.DataFrame(result, columns=["geo_code"]).drop_duplicates()
        data = pd.merge(geo_codes, data, on="geo_code", how="left")

        data = data.replace({np.nan: 0})
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class Childhood(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("childhood", geo_codes)
        return get_childhood(geo_codes, mesh)

