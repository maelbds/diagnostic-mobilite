import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_precarious_jobs(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT pj.CODGEO,
                    pj.act1564prec_nb_all, pj.act1564prec_nb_m, pj.act1564prec_nb_f,
                    pj.act1564prec_part_all, pj.act1564prec_part_m, pj.act1564prec_part_f,
                    pj.act1524prec_part_all, pj.act1524prec_part_m, pj.act1524prec_part_f,
                    pj.act5564prec_part_all, pj.act5564prec_part_m, pj.act5564prec_part_f
                FROM observatoire_insee_rp_emploi_precaire AS pj
                WHERE pj.CODGEO IN :geo_codes 
                AND pj.year_data = :year_pj
            """,
            {
                "geo_codes": geo_codes,
                "year_pj": SOURCE_INSEE_RP,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code",
                                             "act1564prec_nb_all", "act1564prec_nb_m", "act1564prec_nb_f",
                                             "act1564prec_part_all", "act1564prec_part_m", "act1564prec_part_f",
                                             "act1524prec_part_all", "act1524prec_part_m", "act1524prec_part_f",
                                             "act5564prec_part_all", "act5564prec_part_m", "act5564prec_part_f",
                                             ])
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: None})

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT pj.CODGEO,
                    pj.act1564prec_nb_all, pj.act1564prec_nb_m, pj.act1564prec_nb_f,
                    pj.act1564prec_part_all, pj.act1564prec_part_m, pj.act1564prec_part_f,
                    pj.act1524prec_part_all, pj.act1524prec_part_m, pj.act1524prec_part_f,
                    pj.act5564prec_part_all, pj.act5564prec_part_m, pj.act5564prec_part_f
                FROM observatoire_insee_rp_emploi_precaire_epci AS pj
                WHERE pj.CODGEO IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND pj.year_data = :year_pj
            """,
            {
                "geo_codes": geo_codes,
                "year_pj": SOURCE_INSEE_RP,
                "year_epci": SOURCE_EPCI,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code",
                    "act1564prec_nb_all", "act1564prec_nb_m", "act1564prec_nb_f",
                    "act1564prec_part_all", "act1564prec_part_m", "act1564prec_part_f",
                    "act1524prec_part_all", "act1524prec_part_m", "act1524prec_part_f",
                    "act5564prec_part_all", "act5564prec_part_m", "act5564prec_part_f",
                ])

        data = data.replace({np.nan: None})
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class PrecariousJobs(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("precarious jobs", geo_codes)
        return get_precarious_jobs(geo_codes, mesh)

