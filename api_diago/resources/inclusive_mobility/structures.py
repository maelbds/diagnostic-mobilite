import pandas as pd
import numpy as np
import ast

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request
from data_manager.data_inclusion.save_data_inclusion import cols_structures, cols_services


def get_structures(geo_codes):
    result = db_request(
        """ SELECT *
            FROM datainclusion_structures
            WHERE code_insee IN :geo_codes
        """,
        {
            "geo_codes": geo_codes
        }
    )
    structures = pd.DataFrame(result, columns=[c for c in cols_structures if c != "_di_geocodage_code_insee"] + ["saved_on"])
    result = db_request(
         """SELECT *
            FROM datainclusion_structures
            WHERE id IN (SELECT structure_id
                        FROM datainclusion_services
                        WHERE id IN (SELECT id
                                    FROM datainclusion_services_geocodes
                                    WHERE geo_code IN :geo_codes)
                )
        """,
        {
            "geo_codes": geo_codes,
        }
    )
    structures2 = pd.DataFrame(result, columns=[c for c in cols_structures if c != "_di_geocodage_code_insee"] + ["saved_on"])

    structures = pd.concat([structures, structures2]).drop_duplicates(subset="id")

    structures["thematiques"] = [ast.literal_eval(t) for t in structures["thematiques"]]
    structures["date_maj"] = structures["date_maj"].astype(str)

    mask_has_coords = ~structures["longitude"].isna() & ~structures["latitude"].isna()
    structures = structures[mask_has_coords].replace({np.nan: None}).drop(columns=["saved_on"])

    return {
        "structures": structures.to_dict(orient="list")
    }


class Structures(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("structures", geo_codes)
        return get_structures(geo_codes)

