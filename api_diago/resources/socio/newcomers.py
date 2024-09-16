import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_newcomers(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT arr.CODGEO, arr.hh_m2y_nb, arr.hh_m2y_part,
                       ROUND(arr.hh_m2y_avg_size*arr.hh_m2y_nb), arr.hh_m2y_avg_size*arr.hh_m2y_nb/etr.total_pop*100
                FROM observatoire_insee_rp_arrivants AS arr
                JOIN observatoire_insee_rp_etrangers_immigres AS etr ON arr.CODGEO = etr.CODGEO
                WHERE arr.CODGEO IN :geo_codes 
                AND arr.year_data = :year_new
                AND etr.year_data = :year_etr
            """,
            {
                "geo_codes": geo_codes,
                "year_new": SOURCE_INSEE_RP,
                "year_etr": SOURCE_INSEE_RP,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code",
                                             "newcomers_hh_nb", "newcomers_hh_part",
                                             "newcomers_pop_nb", "newcomers_pop_part"])
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data["newcomers_pop_part"] = data["newcomers_pop_part"].round(1)
        data = data.replace({np.nan: None})

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT epci.EPCI,
                       arr.hh_m2y_nb, arr.hh_m2y_part,
                       ROUND(arr.hh_m2y_avg_size*arr.hh_m2y_nb), arr.hh_m2y_avg_size*arr.hh_m2y_nb/etr.total_pop*100
                FROM observatoire_insee_rp_arrivants AS arr
                JOIN observatoire_insee_rp_etrangers_immigres AS etr ON arr.CODGEO = etr.CODGEO
                JOIN insee_epci_communes AS epci ON arr.CODGEO = epci.CODGEO
                WHERE epci.EPCI IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND arr.year_data = :year_new
                AND etr.year_data = :year_etr
                AND epci.year_data = :year_epci
            """,
            {
                "geo_codes": geo_codes,
                "year_new": SOURCE_INSEE_RP,
                "year_etr": SOURCE_INSEE_RP,
                "year_epci": SOURCE_EPCI,
            }
        )

        def agg_func(df):
            return pd.Series({
                "newcomers_hh_nb": df["newcomers_hh_nb"].sum(),
                "newcomers_hh_part": round(
                    df["newcomers_hh_nb"].sum() / (df["newcomers_hh_nb"] / df["newcomers_hh_part"]).sum(), 1)
                if df["newcomers_hh_nb"].sum() > 0 else 0,
                "newcomers_pop_nb": df["newcomers_pop_nb"].sum(),
                "newcomers_pop_part": round(
                    df["newcomers_pop_nb"].sum() / (df["newcomers_pop_nb"] / df["newcomers_pop_part"]).sum(), 1)
                if df["newcomers_pop_nb"].sum() > 0 else 0,
            })

        data = pd.DataFrame(result, columns=["geo_code",
                                             "newcomers_hh_nb", "newcomers_hh_part",
                                             "newcomers_pop_nb", "newcomers_pop_part"])
        data = data.groupby(by="geo_code", as_index=False).apply(lambda df: agg_func(df))
        data = data.replace({np.nan: None})
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class Newcomers(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("newcomers", geo_codes)
        return get_newcomers(geo_codes, mesh)
