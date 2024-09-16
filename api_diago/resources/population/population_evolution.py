import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.insee_local.source import SOURCE_DC_MOBIN
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_population_evolution(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT pop.CODGEO, pop.pop_variation_nb
                FROM observatoire_insee_rp_pop AS pop
                WHERE pop.CODGEO IN :geo_codes 
                AND pop.year_data = :year_rp
            """,
            {
                "geo_codes": geo_codes,
                "year_rp": SOURCE_INSEE_RP,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "pop_variation_nb"])
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: None})

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT epci.EPCI, pop.pop_variation_nb
                FROM observatoire_insee_rp_pop AS pop
                JOIN insee_epci_communes AS epci ON pop.CODGEO = epci.CODGEO
                WHERE epci.EPCI IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND pop.year_data = :year_rp
                AND epci.year_data = :year_epci
            """,
            {
                "geo_codes": geo_codes,
                "year_rp": SOURCE_INSEE_RP,
                "year_epci": SOURCE_EPCI,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "pop_variation_nb"])
        data = data.groupby(by="geo_code", as_index=False).sum()
        data = data.replace({np.nan: None})
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class PopulationEvolution(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("population evolution", geo_codes)
        return get_population_evolution(geo_codes, mesh)

