import pandas as pd
import numpy as np

from api.resources.common.cog import COG
from api.resources.common.log_stats import log_stats
from data_manager.sources.sources import get_years_for_source, get_label_link_for_source_year

from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request

source_label = "geodip_precariousness"

dataset_precariousness = {
    "endpoint": "territory/precariousness",
    "is_mesh_element": True,
    "meshes": ["com"],
    "name_year": "Geodip",
    "years": get_years_for_source(source_label),
}

variables = ["carburant_pourcentage", "logement_carburant_pourcentage"]


def format_result(data):
    data = data.replace({np.nan: None}).round(1)
    return data


def get_precariousness(geo_codes, mesh, year):
    sources = [get_label_link_for_source_year(name, year) for name in [source_label]]

    if mesh == "com":
        result = db_request(
            """ SELECT p.CODGEO_DES, 
                """ + ",".join(variables) + """
                FROM geodip_precariousness AS gp
                JOIN insee_passage_cog AS p ON gp.geo_code = p.CODGEO_INI
                WHERE p.CODGEO_DES IN :geo_codes 
                AND gp.year_data = :year
                AND p.year_cog = :cog
            """,
            {
                "geo_codes": geo_codes,
                "year": year,
                "cog": COG
            }
        )

        data = pd.DataFrame(result, columns=["geo_code"] + variables)
        data = data.drop_duplicates(subset="geo_code", keep=False)
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = format_result(data)

        return {
            "elements": data.to_dict(orient="records"),
            "sources": sources,
            "is_mesh_element": True
        }


class Precariousness(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh
        year = perimeter.year

        log_stats("precariousness", geo_codes, mesh, year)
        message_request("precariousness", geo_codes)
        return get_precariousness(geo_codes, mesh, year)
