import pandas as pd
import numpy as np

from data_manager.ign.source import SOURCE_OUTLINE
from data_manager.pole_emploi.source import SOURCE_POLE_EMPLOI

from shapely.geometry import shape, mapping
from shapely.ops import unary_union

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request
from api_diago.resources.common.utilities import wkb_to_geojson


def get_pole_emploi_communes(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT az.zoneCompetences, d.geo_code_city, az.code
                FROM pole_emploi_agencies_zones AS az
                LEFT JOIN insee_arrondissements AS d ON az.zoneCompetences = d.geo_code_district
                WHERE (az.zoneCompetences IN :geo_codes OR d.geo_code_city IN :geo_codes)
                AND az.year_data = :year_pe
            """,
            {
                "geo_codes": geo_codes,
                "year_pe": SOURCE_POLE_EMPLOI
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "geo_code_city", "agencies"])
        mask_geo_code_city = ~data["geo_code_city"].isna()
        data.loc[mask_geo_code_city, "geo_code"] = data.loc[mask_geo_code_city, "geo_code_city"]
        data = data.drop(columns=["geo_code_city"])
        data = data.groupby("geo_code").agg(lambda col: list(set(col)))
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: None})

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        return {}


def get_pole_emploi_agencies(geo_codes):
    result = db_request(
        """ SELECT ag.code, ag.libelle, ag.type, ag.email, ag.lat, ag.lon
            FROM pole_emploi_agencies_zones AS az
            JOIN pole_emploi_agencies AS ag ON az.code = ag.code
            LEFT JOIN insee_arrondissements AS d ON az.zoneCompetences = d.geo_code_district
            WHERE (az.zoneCompetences IN :geo_codes OR d.geo_code_city IN :geo_codes)
            AND ag.year_data = :year_pe
            AND az.year_data = :year_pe
        """,
        {
            "geo_codes": geo_codes,
            "year_pe": SOURCE_POLE_EMPLOI
        }
    )

    data = pd.DataFrame(result, columns=["code", "name", "type", "email", "lat", "lon"])
    data = data.drop_duplicates(subset="code")
    data["name"] = [n.title() for n in data["name"]]

    return {
        "pe_agencies": data.to_dict(orient="list")
    }


def get_pole_emploi_perimeters(geo_codes):
    result = db_request(
        """ SELECT az.code, az.zoneCompetences, ign.outline
            FROM pole_emploi_agencies_zones AS az
            LEFT JOIN ign_commune_outline AS ign ON az.zoneCompetences = ign.geo_code
            WHERE az.code IN (
                SELECT az2.code
                FROM pole_emploi_agencies_zones AS az2
                LEFT JOIN insee_arrondissements AS d ON az2.zoneCompetences = d.geo_code_district
                WHERE (az2.zoneCompetences IN :geo_codes OR d.geo_code_city IN :geo_codes)
            )
            AND az.year_data = :year_pe
            AND ign.year_cog = :year_ign
        """,
        {
            "geo_codes": geo_codes,
            "year_pe": SOURCE_POLE_EMPLOI,
            "year_ign": SOURCE_OUTLINE
        }
    )

    data = pd.DataFrame(result, columns=["pe_code", "geocode", "outline"])
    data["outline"] = [shape(wkb_to_geojson(outline)) for outline in data["outline"]]
    data = data.groupby(by="pe_code", as_index=False).agg(**{
        "pe_code": pd.NamedAgg(column="pe_code", aggfunc="first"),
        "outline": pd.NamedAgg(column="outline", aggfunc=lambda col: unary_union(col)),
    })
    data["outline"] = [mapping(outline) for outline in data["outline"]]
    data = data.replace({np.nan: None})

    return {
        "pe_perimeters": data.to_dict(orient="list")
    }


class PoleEmploiCommunes(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("pole emploi communes", geo_codes)
        return get_pole_emploi_communes(geo_codes, mesh)


class PoleEmploiAgencies(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("pole emploi agencies", geo_codes)
        return get_pole_emploi_agencies(geo_codes)


class PoleEmploiPerimeters(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("pole emploi perimeters", geo_codes)
        return get_pole_emploi_perimeters(geo_codes)

