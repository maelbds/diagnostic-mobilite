import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.insee_local.source import SOURCE_DC_MOBIN
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_eco_dependance_ind(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT dc.CODGEO,
                    dc.POP, 
                    (dc.POP6074 + dc.POP7589 + dc.POP90P), 
                    (dc.POP2024 + dc.POP2539 + dc.POP4054 + dc.POP5564 + dc.POP6579 + dc.POP80P)
                FROM insee_dossier_complet_mobin AS dc
                WHERE dc.CODGEO IN :geo_codes
                AND dc.year_data = :year_dc
            """,
            {
                "geo_codes": geo_codes,
                "year_dc": SOURCE_DC_MOBIN,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "pop_all", "pop_60p", "pop_20p"])
        data["pop_2059"] = data["pop_20p"] - data["pop_60p"]
        data["eco_dependance_ind"] = (data["pop_all"] - data["pop_2059"]) / data["pop_2059"] * 100
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: None}).round()

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT epci.EPCI,
                    dc.POP, 
                    (dc.POP6074 + dc.POP7589 + dc.POP90P), 
                    (dc.POP2024 + dc.POP2539 + dc.POP4054 + dc.POP5564 + dc.POP6579 + dc.POP80P)
                FROM insee_dossier_complet_mobin AS dc
                JOIN insee_epci_communes AS epci ON dc.CODGEO = epci.CODGEO
                WHERE epci.EPCI IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND dc.year_data = :year_dc
                AND epci.year_data = :year_epci
            """,
            {
                "geo_codes": geo_codes,
                "year_dc": SOURCE_DC_MOBIN,
                "year_epci": SOURCE_EPCI,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "pop_all", "pop_60p", "pop_20p"])
        data = data.groupby(by="geo_code", as_index=False).sum()
        data["pop_2059"] = data["pop_20p"] - data["pop_60p"]
        data["eco_dependance_ind"] = (data["pop_all"] - data["pop_2059"]) / data["pop_2059"] * 100
        data = data.replace({np.nan: None}).round()
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class EcoDependanceInd(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("eco dependance ind", geo_codes)
        return get_eco_dependance_ind(geo_codes, mesh)

