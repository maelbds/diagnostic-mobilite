import pandas as pd
import numpy as np
import geopandas as gpd
import json
from shapely import wkb

from api.resources.common.log_stats import log_stats
from api.resources.common.util_territory import get_neighbors
from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request


dataset_cycle_paths = {
    "endpoint": "offer/cycle_paths",
    "is_mesh_element": False,
    "meshes": None,
    "name_year": None,
    "years": None,
}

variables = ["code_com_g", "code_com_d",
             "ame_d", "ame_g", "sens_d", "sens_g",
             "date_maj", "geometry", "saved_on"]


def get_cycle_paths(geo_codes):
    influence_geocodes = get_neighbors(geo_codes)
    all_geocodes = geo_codes + influence_geocodes

    result = db_request(
        """ SELECT """ + ", ".join([v for v in variables]) + """
            FROM transportdatagouv_cycle_paths AS cp
            LEFT JOIN insee_arrondissements AS arr_g ON cp.code_com_g = arr_g.geo_code_district
            LEFT JOIN insee_arrondissements AS arr_d ON cp.code_com_d = arr_d.geo_code_district 
            WHERE (cp.code_com_g IN :geo_codes OR arr_g.geo_code_city IN :geo_codes
                   OR cp.code_com_d IN :geo_codes OR arr_d.geo_code_city IN :geo_codes) 
        """,
        {
            "geo_codes": all_geocodes
        }
    )

    cycle_paths = pd.DataFrame(result, columns=variables)
    cycle_paths["geometry"] = [wkb.loads(r) for r in cycle_paths["geometry"]]
    cycle_paths["date_maj"] = cycle_paths["date_maj"].astype(str)
    cycle_paths = cycle_paths.replace({np.nan: None})

    result = db_request(
        """ SELECT saved_on
            FROM transportdatagouv_cycle_paths
            LIMIT 1
        """, {})
    saved_on = result.scalar()

    source_data = saved_on.strftime("%m/%Y").title()
    cycle_paths.drop(columns=["saved_on"], inplace=True)

    return {
        "elements": {
            "cycle_paths": json.loads(gpd.GeoDataFrame(cycle_paths).to_json(drop_id=True))
        },
        "sources": [{
            "label": f"Base Nationale des Aménagements Cyclables (OpenStreetMap {source_data})",
            "link": "https://transport.data.gouv.fr/datasets/amenagements-cyclables-france-metropolitaine"
        }],
        "is_mesh_element": False,
    }


class CyclePaths(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes

        log_stats("cycle paths", geo_codes, None, None)
        message_request("cycle paths", geo_codes)
        return get_cycle_paths(geo_codes)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)
    print(get_cycle_paths(["13055"]))

