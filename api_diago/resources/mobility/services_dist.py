import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.insee_local.source import SOURCE_DC_MOBIN
from data_manager.computed.services_dist import categories

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_services_dist(geo_codes, mesh):

    variables = [c+"_dist" for c in categories["cat"].drop_duplicates()]

    if mesh == "com":
        result = db_request(
            """ SELECT s.geo_code,
                """ + ", ".join(["s." + v for v in variables]) + """
                FROM terristory_services_dist AS s
                WHERE s.geo_code IN :geo_codes
            """,
            {
                "geo_codes": geo_codes,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code"] + variables)
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: None})

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT epci.EPCI, dc.POP, 
                """ + ", ".join(["s." + v for v in variables]) + """
                FROM terristory_services_dist AS s
                JOIN insee_epci_communes AS epci ON s.geo_code = epci.CODGEO
                JOIN insee_dossier_complet_mobin AS dc ON s.geo_code = dc.CODGEO
                WHERE epci.EPCI IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND epci.year_data = :year_epci
                AND dc.year_data = :year_dc
            """,
            {
                "geo_codes": geo_codes,
                "year_dc": SOURCE_DC_MOBIN,
                "year_epci": SOURCE_EPCI,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "pop"] + variables)
        data[variables] = data[variables].multiply(data["pop"], axis=0)
        data = data.groupby(by="geo_code", as_index=False).sum()
        data[variables] = data[variables].div(data["pop"], axis=0)
        data = data.replace({np.nan: None}).round(2)
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class ServicesDist(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("services dist", geo_codes)
        return get_services_dist(geo_codes, mesh)

