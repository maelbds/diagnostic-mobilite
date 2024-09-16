import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP, \
    SOURCE_FILOSOFI, SOURCE_CNAF_FILEAS, SOURCE_INSEE_DREES

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_allocation(geo_codes, mesh):
    if mesh == "dep":
        result = db_request(
            """ SELECT apa.CODGEO, dep.LIBELLE,
                       apa.beneficiaries_apa_nb, apa.beneficiaries_apa_part,
                       old.beneficiaries_min_old_age_nb, old.beneficiaries_min_old_age_part
                FROM observatoire_cnaf_fileas_apa AS apa
                JOIN observatoire_insee_drees_old_age AS old ON old.CODGEO = apa.CODGEO
                JOIN insee_cog_departements AS dep ON dep.DEP = apa.CODGEO 
                WHERE apa.CODGEO IN (
                    SELECT com.DEP
                    FROM insee_cog_communes AS com
                    WHERE com.COM IN :geo_codes 
                    AND com.year_data = :year_cog
                  ) 
                AND apa.year_data = :year_apa
                AND old.year_data = :year_old
            """,
            {
                "geo_codes": geo_codes,
                "year_cog": SOURCE_EPCI,
                "year_apa": SOURCE_CNAF_FILEAS,
                "year_old": SOURCE_INSEE_DREES,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "name",
                                             "beneficiaries_apa_nb", "beneficiaries_apa_part",
                                             "beneficiaries_min_old_age_nb", "beneficiaries_min_old_age_part"])
        data = data.replace({np.nan: None})
        data = data.sort_values(by="geo_code")

        return {
            "dep": data.to_dict(orient="list")
        }

    else:
        return {}


class Allocation(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("allocation", geo_codes)
        return get_allocation(geo_codes, mesh)
