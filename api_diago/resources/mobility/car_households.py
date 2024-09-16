import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.insee_local.source import SOURCE_DC_MOBIN

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_car_households(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT dc.CODGEO, dc.RP_VOIT1P, dc.MEN
                FROM insee_dossier_complet_mobin AS dc
                WHERE dc.CODGEO IN :geo_codes
                AND dc.year_data = :year_dc
            """,
            {
                "geo_codes": geo_codes,
                "year_dc": SOURCE_DC_MOBIN,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "hh_with_car_nb", "hh_all_nb"])
        data["hh_all_nb"] = [max(hh_all, hh_car) for hh_all, hh_car in zip(data["hh_all_nb"], data["hh_with_car_nb"])]
        data["hh_with_car_prop"] = data["hh_with_car_nb"] / data["hh_all_nb"] * 100
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: None}).round(1)

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT epci.EPCI, dc.RP_VOIT1P, dc.MEN
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

        data = pd.DataFrame(result, columns=["geo_code", "hh_with_car_nb", "hh_all_nb"])
        data = data.groupby(by="geo_code", as_index=False).sum()
        data["hh_with_car_prop"] = data["hh_with_car_nb"] / data["hh_all_nb"] * 100
        data = data.replace({np.nan: None}).round(1)
        data = data.sort_values(by="geo_code")

        return {
            "epci": data.to_dict(orient="list")
        }


class CarHouseholds(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("car households", geo_codes)
        return get_car_households(geo_codes, mesh)

