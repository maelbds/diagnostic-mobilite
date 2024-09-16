import pandas as pd
import numpy as np
import ast

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request
from data_manager.data_inclusion.save_data_inclusion import cols_structures, cols_services


def get_services(geo_codes):
    result = db_request(
        """ SELECT *
            FROM datainclusion_services
            WHERE id IN (SELECT id 
                         FROM datainclusion_services_geocodes 
                         WHERE geo_code IN :geo_codes)
        """,
        {
            "geo_codes": geo_codes
        }
    )

    services = pd.DataFrame(result, columns=cols_services + ["saved_on"])
    services = services.drop_duplicates(subset=["id"])#.drop(columns=["id_bis", "geo_code"])

    services["thematiques"] = [ast.literal_eval(t) for t in services["thematiques"]]
    services["date_maj"] = services["date_maj"].astype(str)
    services["date_suspension"] = services["date_suspension"].astype(str)

    services = services.replace({np.nan: None}).drop(columns=["saved_on"])

    return {
        "services": services.to_dict(orient="list")
    }


def get_services_geocodes(geo_codes):
    result = db_request(
        """ SELECT id, geo_code
            FROM datainclusion_services_geocodes 
            WHERE geo_code IN :geo_codes
        """,
        {
            "geo_codes": geo_codes
        }
    )

    services = pd.DataFrame(result, columns=["structure_id", "geo_code"])
    services = services.groupby("geo_code", as_index=False).agg(list)

    services = pd.merge(pd.DataFrame({"geo_code": geo_codes}), services, on="geo_code", how="left")
    services = services.replace({np.nan: None})

    return {
        "services_geocodes": services.to_dict(orient="list")
    }


class Services(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("services", geo_codes)
        return get_services(geo_codes)


class ServicesGeocodes(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("services geocodes", geo_codes)
        return get_services_geocodes(geo_codes)

