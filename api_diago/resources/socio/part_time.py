import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_part_time(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT pj.CODGEO,
                    pj.act1564tp_nb_all, pj.act1564tp_nb_m, pj.act1564tp_nb_f,
                    pj.act1564tp_part_all, pj.act1564tp_part_m, pj.act1564tp_part_f,
                    pj.act1524tp_part_all, pj.act1524tp_part_m, pj.act1524tp_part_f,
                    pj.act5564tp_part_all, pj.act5564tp_part_m, pj.act5564tp_part_f
                FROM observatoire_insee_rp_emploi_partiel AS pj
                WHERE pj.CODGEO IN :geo_codes
                AND pj.year_data = :year_pt
            """,
            {
                "geo_codes": geo_codes,
                "year_pt": SOURCE_INSEE_RP,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code",
                                             "act1564tp_nb_all", "act1564tp_nb_m", "act1564tp_nb_f",
                                             "act1564tp_part_all", "act1564tp_part_m", "act1564tp_part_f",
                                             "act1524tp_part_all", "act1524tp_part_m", "act1524tp_part_f",
                                             "act5564tp_part_all", "act5564tp_part_m", "act5564tp_part_f",
                                             ])
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: None})

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT pj.CODGEO,
                    pj.act1564tp_nb_all, pj.act1564tp_nb_m, pj.act1564tp_nb_f,
                    pj.act1564tp_part_all, pj.act1564tp_part_m, pj.act1564tp_part_f,
                    pj.act1524tp_part_all, pj.act1524tp_part_m, pj.act1524tp_part_f,
                    pj.act5564tp_part_all, pj.act5564tp_part_m, pj.act5564tp_part_f
                FROM observatoire_insee_rp_emploi_partiel_epci AS pj
                WHERE pj.CODGEO IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND pj.year_data = :year_pt
            """,
            {
                "geo_codes": geo_codes,
                "year_pt": SOURCE_INSEE_RP,
                "year_epci": SOURCE_EPCI,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code",
                                             "act1564tp_nb_all", "act1564tp_nb_m", "act1564tp_nb_f",
                                             "act1564tp_part_all", "act1564tp_part_m", "act1564tp_part_f",
                                             "act1524tp_part_all", "act1524tp_part_m", "act1524tp_part_f",
                                             "act5564tp_part_all", "act5564tp_part_m", "act5564tp_part_f",
                                             ])

        data = data.replace({np.nan: None}).round(1)
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class PartTime(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("part time", geo_codes)
        return get_part_time(geo_codes, mesh)

