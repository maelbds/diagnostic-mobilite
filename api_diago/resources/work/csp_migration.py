import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP, \
    SOURCE_FILOSOFI, SOURCE_CNAF_FILEAS, SOURCE_INSEE_DREES, SOURCE_SOLDE_MIG

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_csp_migration(geo_codes, mesh):

    variables = ["solde_mig_CS"+str(i) for i in range(1, 9)]

    if mesh == "dep":
        result = db_request(
            """ SELECT sm.CODGEO, dep.LIBELLE, 
                """ + ",".join(["sm." + v for v in variables]) + """
                FROM observatoire_insee_rp_solde_migratoire_csp_dep AS sm
                JOIN insee_cog_departements AS dep ON dep.DEP = sm.CODGEO 
                WHERE sm.CODGEO IN (
                    SELECT com.DEP
                    FROM insee_cog_communes AS com
                    WHERE com.COM IN :geo_codes
                    AND com.year_data = :year_cog
                  ) 
                AND sm.year_data = :year_sm
                AND dep.year_data = :year_cog
            """,
            {
                "geo_codes": geo_codes,
                "year_cog": SOURCE_EPCI,
                "year_sm": SOURCE_SOLDE_MIG,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "name"] + variables)
        data = data.replace({np.nan: None})
        data = data.sort_values(by="geo_code")

        return {
            "dep": data.to_dict(orient="list")
        }

    else:
        return {}


class CSPMigration(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("csp_migration", geo_codes)
        return get_csp_migration(geo_codes, mesh)
