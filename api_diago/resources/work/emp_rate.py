import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_emp_rate(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT emp.CODGEO,
                        emp.emp_rate_1564_all, emp.emp_rate_1564_m, emp.emp_rate_1564_f,
                        emp.emp_rate_1524_all, emp.emp_rate_1524_m, emp.emp_rate_1524_f,
                        emp.emp_rate_5564_all, emp.emp_rate_5564_m, emp.emp_rate_5564_f
                FROM observatoire_insee_rp_emploi AS emp
                WHERE emp.CODGEO IN :geo_codes
                AND emp.year_data = :year_emp
            """,
            {
                "geo_codes": geo_codes,
                "year_emp": SOURCE_INSEE_RP,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code",
                                             "emp_rate_1564_all", "emp_rate_1564_m", "emp_rate_1564_f",
                                             "emp_rate_1524_all", "emp_rate_1524_m", "emp_rate_1524_f",
                                             "emp_rate_5564_all", "emp_rate_5564_m", "emp_rate_5564_f",
                                             ])
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: None})

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT emp.CODGEO,
                        emp.emp_rate_1564_all, emp.emp_rate_1564_m, emp.emp_rate_1564_f,
                        emp.emp_rate_1524_all, emp.emp_rate_1524_m, emp.emp_rate_1524_f,
                        emp.emp_rate_5564_all, emp.emp_rate_5564_m, emp.emp_rate_5564_f
                FROM observatoire_insee_rp_taux_emploi_epci AS emp
                WHERE emp.CODGEO IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes 
                    AND epci2.year_data = :year_epci
                  ) 
                AND emp.year_data = :year_emp
            """,
            {
                "geo_codes": geo_codes,
                "year_emp": SOURCE_INSEE_RP,
                "year_epci": SOURCE_EPCI,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code",
                                             "emp_rate_1564_all", "emp_rate_1564_m", "emp_rate_1564_f",
                                             "emp_rate_1524_all", "emp_rate_1524_m", "emp_rate_1524_f",
                                             "emp_rate_5564_all", "emp_rate_5564_m", "emp_rate_5564_f",
                                             ])

        data = data.replace({np.nan: None})
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class EmpRate(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("emp rate", geo_codes)
        return get_emp_rate(geo_codes, mesh)

