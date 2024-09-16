import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP, SOURCE_QPV

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_qpv(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT qpv.CODGEO, qpv.qpv_pop, qpv.qpv_part_pop, qpv.qpv_nb
                FROM observatoire_insee_rp_anct_qpv AS qpv
                WHERE qpv.CODGEO IN :geo_codes
                AND qpv.year_data = :year_qpv
            """,
            {
                "geo_codes": geo_codes,
                "year_qpv": SOURCE_QPV,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "qpv_pop", "qpv_part_pop", "qpv_nb"])
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: 0})
        data["qpv_nb"] = data["qpv_nb"].fillna(value=0)

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT epci.EPCI, qpv.qpv_pop, qpv.qpv_part_pop, qpv.qpv_nb
                FROM observatoire_insee_rp_anct_qpv AS qpv
                JOIN insee_epci_communes AS epci ON qpv.CODGEO = epci.CODGEO
                WHERE epci.EPCI IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND qpv.year_data = :year_qpv
                AND epci.year_data = :year_epci
            """,
            {
                "geo_codes": geo_codes,
                "year_qpv": SOURCE_QPV,
                "year_epci": SOURCE_EPCI,
            }
        )

        def agg_func(df):
            return pd.Series({
                "qpv_nb": df["qpv_nb"].sum(),
                "qpv_pop": df["qpv_pop"].sum(),
                "qpv_part_pop": round(df["qpv_pop"].sum() / (df["qpv_pop"] / df["qpv_part_pop"]).sum(), 1)
                                if df["qpv_pop"].sum() > 0 else 0,
            })

        data = pd.DataFrame(result, columns=["geo_code", "qpv_pop", "qpv_part_pop", "qpv_nb"])
        data = data.groupby(by="geo_code", as_index=False).apply(lambda df: agg_func(df))
        data = data.replace({np.nan: 0})
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class QPV(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("qpv", geo_codes)
        return get_qpv(geo_codes, mesh)

