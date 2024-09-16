import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_jobs_applicants(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT emp.CODGEO, emp.jobs_applicants_ABC_nb_all, 

                    ROUND(emp.jobs_applicants_ABC_nb_all * emp.jobs_applicants_ABC_part_m25y / 100), 
                    emp.jobs_applicants_ABC_part_m25y, 

                    ROUND(emp.jobs_applicants_ABC_nb_all * emp.jobs_applicants_ABC_part_p50y / 100),
                    emp.jobs_applicants_ABC_part_p50y

                FROM observatoire_dares_demandeurs_emploi AS emp
                WHERE emp.CODGEO IN :geo_codes
                AND emp.year_data = :year_emp
            """,
            {
                "geo_codes": geo_codes,
                "year_emp": SOURCE_DARES,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code",
            "jobs_applicants_ABC_nb_all", "jobs_applicants_ABC_nb_m25y", "jobs_applicants_ABC_part_m25y",
            "jobs_applicants_ABC_nb_p50y", "jobs_applicants_ABC_part_p50y"])
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: None})

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT epci.EPCI, emp.jobs_applicants_ABC_nb_all, 

                        ROUND(emp.jobs_applicants_ABC_nb_all * emp.jobs_applicants_ABC_part_m25y / 100), 
                        emp.jobs_applicants_ABC_part_m25y, 

                        ROUND(emp.jobs_applicants_ABC_nb_all * emp.jobs_applicants_ABC_part_p50y / 100),
                        emp.jobs_applicants_ABC_part_p50y

                FROM observatoire_dares_demandeurs_emploi AS emp
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
                "year_emp": SOURCE_DARES,
                "year_epci": SOURCE_EPCI,
            }
        )

        def agg_func(df):
            return pd.Series({
                "jobs_applicants_ABC_nb_all": df["jobs_applicants_ABC_nb_all"].sum(),
                "jobs_applicants_ABC_nb_m25y": df["jobs_applicants_ABC_nb_m25y"].sum(),
                "jobs_applicants_ABC_nb_p50y": df["jobs_applicants_ABC_nb_p50y"].sum(),
                "jobs_applicants_ABC_part_m25y": df["jobs_applicants_ABC_nb_m25y"].sum() / df[
                    "jobs_applicants_ABC_nb_all"].sum() * 100,
                "jobs_applicants_ABC_part_p50y": df["jobs_applicants_ABC_nb_p50y"].sum() / df[
                    "jobs_applicants_ABC_nb_all"].sum() * 100,
            })

        data = pd.DataFrame(result, columns=["geo_code",
            "jobs_applicants_ABC_nb_all", "jobs_applicants_ABC_nb_m25y", "jobs_applicants_ABC_part_m25y",
            "jobs_applicants_ABC_nb_p50y", "jobs_applicants_ABC_part_p50y"])
        data = data.groupby(by="geo_code", as_index=False).apply(lambda df: agg_func(df))
        data = data.replace({np.nan: None}).round(1)
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class JobsApplicants(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("jobs applicants", geo_codes)
        return get_jobs_applicants(geo_codes, mesh)

