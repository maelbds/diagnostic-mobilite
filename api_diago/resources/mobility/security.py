import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.observatoire_territoire.source import SOURCE_ONISR
from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_security(geo_codes):
    result = db_request(
        """ SELECT  sr.CODGEO, dep.LIBELLE, 
                    sr.road_death_nb, sr.evol_rate_road_death,
                    sr.rate_road_death_1824, sr.rate_road_death_all
            FROM observatoire_onisr_securite_routiere_dep AS sr
            JOIN insee_cog_departements AS dep ON dep.DEP = sr.CODGEO 
            WHERE sr.CODGEO IN (
                SELECT com.DEP
                FROM insee_cog_communes AS com
                WHERE com.COM IN :geo_codes
                AND com.year_data = :year_epci
              ) 
            AND sr.year_data = :year_sr
            AND dep.year_data = :year_epci
        """,
        {
            "geo_codes": geo_codes,
            "year_sr": SOURCE_ONISR,
            "year_epci": SOURCE_EPCI,
        }
    )

    data = pd.DataFrame(result, columns=["geo_code", "name",
                                         "road_death_nb", "evol_rate_road_death",
                                         "rate_road_death_1824", "rate_road_death_all"])
    data = data.replace({np.nan: None}).round(2)
    data = data.sort_values(by="geo_code")

    return {
        "security": data.to_dict(orient="list")
    }


class Security(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("security", geo_codes)
        return get_security(geo_codes)

