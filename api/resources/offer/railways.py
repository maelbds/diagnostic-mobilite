import pandas as pd
import geopandas as gpd
import json

from shapely import wkb
from shapely.ops import unary_union


from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.log_stats import log_stats
from api.resources.common.schema_request import context_get_request


dataset_railways = {
    "endpoint": "offer/railways",
    "is_mesh_element": False,
    "meshes": None,
    "name_year": None,
    "years": None,
}


def get_railways(geo_codes):
    result = db_request(
        """ SELECT lib_ligne, geometry
            FROM sncf_railways
            WHERE lib_ligne IN (SELECT lib_ligne
                                FROM sncf_railways_communes
                                WHERE CODGEO IN :geo_codes)
        """,
        {
            "geo_codes": geo_codes,
        }
    )

    railways = pd.DataFrame(result, columns=["name", "geometry"])
    railways["geometry_shape"] = [wkb.loads(r) for r in railways["geometry"]]
    railways = railways.groupby(by="name", as_index=False).agg(**{
        "geometry": pd.NamedAgg(column="geometry_shape", aggfunc=lambda col: unary_union(col)),
    })

    return {
        "elements": {
            "railways": json.loads(gpd.GeoDataFrame(railways).to_json(drop_id=True))
        },
        "sources": {
            "label": "Lignes par région administrative (SNCF 2023)",
            "link": "https://ressources.data.sncf.com/explore/dataset/lignes-par-region-administrative/table/"
        },
        "is_mesh_element": False,
    }


class Railways(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes

        log_stats("railways", geo_codes, None, None)
        message_request("railways", geo_codes)
        return get_railways(geo_codes)
