import pandas as pd
import numpy as np

from data_manager.ign.source import SOURCE_OUTLINE
from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.observatoire_territoire.source import SOURCE_DG_COLL

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_budget_com(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT bud.CODGEO,
                       bud.equalization_budget_per_hab,
                       bud.equalization_budget_part_operation
                FROM observatoire_dg_collectivites_budget_com AS bud
                WHERE bud.CODGEO IN :geo_codes
                AND bud.year_data = :year_bud
            """,
            {
                "geo_codes": geo_codes,
                "year_bud": SOURCE_DG_COLL
            }
        )

        data = pd.DataFrame(result, columns=["geo_code",
                                             "equalization_budget_per_hab",
                                             "equalization_budget_part_operation"])
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: 0})

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT bud.CODGEO,
                       bud.equalization_budget_per_hab,
                       bud.equalization_budget_part_operation
                FROM observatoire_dg_collectivites_budget_epci AS bud
                WHERE bud.CODGEO IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND bud.year_data = :year_bud
            """,
            {
                "geo_codes": geo_codes,
                "year_epci": SOURCE_EPCI,
                "year_bud": SOURCE_DG_COLL
            }
        )
        data = pd.DataFrame(result, columns=["geo_code",
                                             "equalization_budget_per_hab",
                                             "equalization_budget_part_operation"])
        data["equalization_budget_per_hab"] = None
        data["equalization_budget_part_operation"] = None
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


def get_budget_epci(geo_codes, mesh):
    if mesh == "com":
        data = pd.DataFrame({"geo_code": geo_codes})
        data["equalization_budget_per_hab"] = None
        data["equalization_budget_part_operation"] = None

        return {
                "com": data.to_dict(orient="list")
            }

    elif mesh == "epci":
        result = db_request(
            """ SELECT bud.CODGEO,
                       bud.equalization_budget_per_hab,
                       bud.equalization_budget_part_operation
                FROM observatoire_dg_collectivites_budget_epci AS bud
                WHERE bud.CODGEO IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND bud.year_data = :year_bud
            """,
            {
                "geo_codes": geo_codes,
                "year_epci": SOURCE_EPCI,
                "year_bud": SOURCE_DG_COLL
            }
        )

        data = pd.DataFrame(result, columns=["geo_code",
                                             "equalization_budget_per_hab",
                                             "equalization_budget_part_operation"])
        data = data.replace({np.nan: None})
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class BudgetCom(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("budget_com", geo_codes)
        return get_budget_com(geo_codes, mesh)


class BudgetEpci(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("budget_epci", geo_codes)
        return get_budget_epci(geo_codes, mesh)

