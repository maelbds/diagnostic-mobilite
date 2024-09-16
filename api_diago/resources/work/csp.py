import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.insee_local.source import SOURCE_DC_MOBIN
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_csp(geo_codes, mesh):

    variables_all = ["POP15P_CS"+str(i) for i in range(1, 9)]
    variables_m = ["H15P_CS"+str(i) for i in range(1, 9)]
    variables_f = ["F15P_CS"+str(i) for i in range(1, 9)]

    if mesh == "com":
        result = db_request(
            """ SELECT dc.CODGEO,
                """ + ",".join(["dc." + v for v in variables_all + variables_m + variables_f]) + """
                FROM insee_dossier_complet_mobin AS dc
                WHERE dc.CODGEO IN :geo_codes
                AND dc.year_data = :year_dc
            """,
            {
                "geo_codes": geo_codes,
                "year_dc": SOURCE_DC_MOBIN,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code"] + variables_all + variables_m + variables_f)
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data["POP15P"] = data[variables_all].sum(axis=1)
        data["H15P"] = data[variables_m].sum(axis=1)
        data["F15P"] = data[variables_f].sum(axis=1)
        data = data.replace({np.nan: None})
        data = data.rename(columns=lambda name: name.replace("POP", "all").replace("H", "m").replace("F", "f"))

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT epci.EPCI,
                """ + ",".join(["dc." + v for v in variables_all + variables_m + variables_f]) + """
                FROM insee_dossier_complet_mobin AS dc
                JOIN insee_epci_communes AS epci ON dc.CODGEO = epci.CODGEO
                WHERE epci.EPCI IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND dc.year_data = :year_dc
                AND epci.year_data = :year_epci
            """,
            {
                "geo_codes": geo_codes,
                "year_dc": SOURCE_DC_MOBIN,
                "year_epci": SOURCE_EPCI,
            }
        )

        def agg_func(df):
            return pd.Series(
                {v: df[v].sum() for v in variables_all + variables_m + variables_f}
            )

        data = pd.DataFrame(result, columns=["geo_code"] + variables_all + variables_m + variables_f)
        data = data.groupby(by="geo_code", as_index=False).apply(lambda df: agg_func(df))
        data["POP15P"] = data[variables_all].sum(axis=1)
        data["H15P"] = data[variables_m].sum(axis=1)
        data["F15P"] = data[variables_f].sum(axis=1)
        data = data.replace({np.nan: None})
        data = data.rename(columns=lambda name: name.replace("POP", "all").replace("H", "m").replace("F", "f"))
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class CSP(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("csp", geo_codes)
        return get_csp(geo_codes, mesh)

