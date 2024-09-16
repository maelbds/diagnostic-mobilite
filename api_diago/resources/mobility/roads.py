import pandas as pd
from shapely.geometry import shape, mapping
from shapely import wkb
from shapely.ops import unary_union

from data_manager.ign.source import SOURCE_ROADS

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_roads(geo_codes):
    result = db_request(
        """ SELECT NUM_ROUTE, CLASS_ADM, geometry
            FROM ign_routes
            WHERE NUM_ROUTE IN (SELECT NUM_ROUTE
                                FROM ign_routes_communes
                                WHERE CODGEO IN :geo_codes
                                AND year_data = :year_roads)
            AND year_data = :year_roads
        """,
        {
            "geo_codes": geo_codes,
            "year_roads": SOURCE_ROADS
        }
    )

    roads = pd.DataFrame(result, columns=["name", "type", "geometry"])
    roads["geometry_shape"] = [wkb.loads(r) for r in roads["geometry"]]
    roads = roads.groupby(by="name", as_index=False).agg(**{
        "type": pd.NamedAgg(column="type", aggfunc=lambda col: col.mode().iloc[0]),
        "geometry": pd.NamedAgg(column="geometry_shape", aggfunc=lambda col: mapping(unary_union(col))),
    })

    return {
        "roads": roads.to_dict(orient="list")
    }


class Roads(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("roads", geo_codes)
        return get_roads(geo_codes)

