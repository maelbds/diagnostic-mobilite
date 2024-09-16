import pandas as pd
from shapely.geometry import shape, mapping
from shapely import wkb
from shapely.ops import unary_union

from data_manager.sncf.source import SOURCE_RAILWAYS

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_railways(geo_codes):
    result = db_request(
        """ SELECT lib_ligne, geometry
            FROM sncf_railways
            WHERE lib_ligne IN (SELECT lib_ligne
                                FROM sncf_railways_communes
                                WHERE CODGEO IN :geo_codes
                                AND year_data = :year_railways)
            AND year_data = :year_railways
        """,
        {
            "geo_codes": geo_codes,
            "year_railways": SOURCE_RAILWAYS
        }
    )

    railways = pd.DataFrame(result, columns=["name", "geometry"])
    railways["geometry_shape"] = [wkb.loads(r) for r in railways["geometry"]]
    railways = railways.groupby(by="name", as_index=False).agg(**{
        "geometry": pd.NamedAgg(column="geometry_shape", aggfunc=lambda col: mapping(unary_union(col))),
    })

    return {
        "railways": railways.to_dict(orient="list")
    }


class Railways(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("railways", geo_codes)
        return get_railways(geo_codes)

