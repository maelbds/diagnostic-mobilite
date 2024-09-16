import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_jobs_organisation(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT emp.CODGEO, emp.jobs_concentration, emp.act_outside_res_com_part, emp.unemployment_rate
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
                                             "jobs_concentration", "act_outside_res_com_part", "unemployment_rate"
                                             ])
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: None})

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT epci.EPCI,
                        emp.jobs_nb, emp.jobs_concentration, (emp.jobs_nb/emp.jobs_concentration*100),
                        emp.act_outside_res_com_part, emp.unemployment_rate, emp.unemployment_nb
                FROM observatoire_insee_rp_emploi AS emp
                JOIN insee_epci_communes AS epci ON emp.CODGEO = epci.CODGEO
                WHERE epci.EPCI IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND emp.year_data = :year_emp
                AND epci.year_data = :year_epci
            """,
            {
                "geo_codes": geo_codes,
                "year_emp": SOURCE_INSEE_RP,
                "year_epci": SOURCE_EPCI,
            }
        )

        def agg_func(df):
            return pd.Series({
                "jobs_concentration": df["jobs_nb"].sum() / df["pop_act"].sum() * 100,
                "act_outside_res_com_part": (df["act_outside_res_com_part"] * df["pop_act"]).sum() / df[
                    "pop_act"].sum(),
                "unemployment_rate": df["unemployment_nb"].sum() / (
                        df["unemployment_nb"] / df["unemployment_rate"]).sum()
            })

        data = pd.DataFrame(result, columns=["geo_code",
                                             "jobs_nb", "jobs_concentration", "pop_act", "act_outside_res_com_part",
                                             "unemployment_rate", "unemployment_nb"
                                             ])
        data = data.groupby(by="geo_code", as_index=False).apply(lambda df: agg_func(df))
        data = data.replace({np.nan: None}).round(1)
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class JobsOrganisation(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("jobs organisation", geo_codes)
        return get_jobs_organisation(geo_codes, mesh)

