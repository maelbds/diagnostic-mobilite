import pandas as pd
import numpy as np

from data_manager.transportdatagouv.source import SOURCE_CYCLE_PATHS, SOURCE_CYCLE_PARKINGS

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request
from api_diago.resources.common.utilities import wkb_to_geojson


def get_cycle_paths(geo_codes):
    result = db_request(
        """ SELECT id_local, id_osm, code_com_g, code_com_d, 
                   ame_d, ame_g, sens_d, sens_g, 
                   source, date_maj, geometry
            FROM transportdatagouv_cycle_paths 
            WHERE ((code_com_g IN :geo_codes 
                   OR code_com_d IN :geo_codes) 
            AND source = :source_cp)
        """,
        {
            "geo_codes": geo_codes,
            "source_cp": SOURCE_CYCLE_PATHS
        }
    )

    all_cycle_paths = pd.DataFrame(result, columns=["id_local", "id_osm", "code_com_g", "code_com_d",
                                                    "ame_d", "ame_g", "sens_d", "sens_g",
                                                    "source", "date_maj", "geometry"])

    all_cycle_paths["geometry"] = [wkb_to_geojson(r) for r in all_cycle_paths["geometry"]]
    all_cycle_paths["date_maj"] = all_cycle_paths["date_maj"].astype(str)
    all_cycle_paths = all_cycle_paths.replace({np.nan: None})

    return {
        "cycle_paths": all_cycle_paths.to_dict(orient="list")
    }


def get_cycle_parkings(geo_codes):
    result = db_request(
        """ SELECT id, code_com, lat, lon, 
                   capacite, gestionnaire, date_maj
            FROM transportdatagouv_cycle_parkings 
            WHERE code_com IN :geo_codes
            AND source = :source_cp
        """,
        {
            "geo_codes": geo_codes,
            "source_cp": SOURCE_CYCLE_PARKINGS
        }
    )

    cycle_parkings = pd.DataFrame(result, columns=["id", "code_com", "lat", "lon",
                                                   "capacite", "gestionnaire", "date_maj"])

    cycle_parkings["capacite"] = cycle_parkings["capacite"].replace({np.nan: None})
    cycle_parkings["date_maj"] = cycle_parkings["date_maj"].astype(str)

    return {
        "cycle_parkings": cycle_parkings.to_dict(orient="list")
    }


class CyclePaths(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("cycle paths", geo_codes)
        return get_cycle_paths(geo_codes)


class CycleParkings(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("cycle parkings", geo_codes)
        return get_cycle_parkings(geo_codes)

