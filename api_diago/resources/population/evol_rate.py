import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.insee_local.source import SOURCE_DC_MOBIN
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP, \
    SOURCE_EVOL_RATE_FUTURE

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_evol_rate(geo_codes, mesh):
    if mesh == "dep":
        result = db_request(
            """ SELECT ef.CODGEO, dep.LIBELLE, ef.evol_rate_pop, ep.evol_rate_pop
                FROM observatoire_insee_rp_pop_evolution_futur_dep AS ef
                JOIN observatoire_insee_rp_pop_evolution_passe_dep AS ep ON ef.CODGEO = ep.CODGEO
                JOIN insee_cog_departements AS dep ON dep.DEP = ef.CODGEO 
                WHERE ef.CODGEO IN (
                    SELECT com.DEP
                    FROM insee_cog_communes AS com
                    WHERE com.COM IN :geo_codes
                    AND com.year_data = :year_cog
                  ) 
                AND ep.year_data = :year_rp
                AND ef.year_data = :year_evol
                AND dep.year_data = :year_cog
            """,
            {
                "geo_codes": geo_codes,
                "year_rp": SOURCE_INSEE_RP,
                "year_evol": SOURCE_EVOL_RATE_FUTURE,
                "year_cog": SOURCE_EPCI,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "name", "evol_rate_future", "evol_rate_past"])
        data = data.replace({np.nan: None}).round(2)
        data = data.sort_values(by="geo_code")

        return {
            "dep": data.to_dict(orient="list")
        }

    else:
        return {}


class EvolRate(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("evol rate", geo_codes)
        return get_evol_rate(geo_codes, mesh)

