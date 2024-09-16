import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_foreigners(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT etr.CODGEO,
                        etr.foreigners_part, ROUND(etr.total_pop*etr.foreigners_part/100), 
                        etr.immigrants_part, ROUND(etr.total_pop*etr.immigrants_part/100)
                FROM observatoire_insee_rp_etrangers_immigres AS etr
                WHERE etr.CODGEO IN :geo_codes
                AND etr.year_data = :year_etr
            """,
            {
                "geo_codes": geo_codes,
                "year_etr": SOURCE_INSEE_RP,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code",
                                             "foreigners_part", "foreigners_nb",
                                             "immigrants_part", "immigrants_nb"])
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: None})

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT epci.EPCI,
                    etr.foreigners_part, ROUND(etr.total_pop*etr.foreigners_part/100), 
                    etr.immigrants_part, ROUND(etr.total_pop*etr.immigrants_part/100)
                FROM observatoire_insee_rp_etrangers_immigres AS etr
                JOIN insee_epci_communes AS epci ON etr.CODGEO = epci.CODGEO
                WHERE epci.EPCI IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND etr.year_data = :year_etr
                AND epci.year_data = :year_epci
            """,
            {
                "geo_codes": geo_codes,
                "year_etr": SOURCE_INSEE_RP,
                "year_epci": SOURCE_EPCI,
            }
        )

        def agg_func(df):
            return pd.Series({
                "foreigners_nb": df["foreigners_nb"].sum(),
                "foreigners_part": round(
                    df["foreigners_nb"].sum() / (df["foreigners_nb"] / df["foreigners_part"]).sum(), 1)
                if df["foreigners_nb"].sum() > 0 else 0,
                "immigrants_nb": df["immigrants_nb"].sum(),
                "immigrants_part": round(
                    df["immigrants_nb"].sum() / (df["immigrants_nb"] / df["immigrants_part"]).sum(), 1)
                if df["immigrants_nb"].sum() > 0 else 0,
            })

        data = pd.DataFrame(result, columns=["geo_code",
                                             "foreigners_part", "foreigners_nb",
                                             "immigrants_part", "immigrants_nb"])
        data = data.groupby(by="geo_code", as_index=False).apply(lambda df: agg_func(df))
        data = data.replace({np.nan: None})
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class Foreigners(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("foreigners", geo_codes)
        return get_foreigners(geo_codes, mesh)
