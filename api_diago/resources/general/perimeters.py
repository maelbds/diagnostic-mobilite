import pandas as pd
import numpy as np
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

from data_manager.ign.source import SOURCE_OUTLINE
from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.observatoire_territoire.source import SOURCE_PNR, SOURCE_PETR, SOURCE_ZRR

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request
from api_diago.resources.common.utilities import wkb_to_geojson


def get_arrondissements(geo_codes):
    result = db_request(
        """ SELECT cog.COM, ign_o.outline, cog.ARR, arr.LIBELLE
            FROM insee_cog_communes AS cog
            LEFT JOIN ign_commune_outline AS ign_o ON cog.COM = ign_o.geo_code
            LEFT JOIN insee_cog_arrondissements AS arr ON cog.ARR = arr.ARR
            WHERE cog.ARR IN (
                SELECT cog2.ARR
                FROM insee_cog_communes AS cog2
                WHERE cog2.COM IN :geo_codes
                AND cog2.year_cog = :year_cog
              )
            AND cog.year_cog = :year_cog AND ign_o.year_cog = :year_cog AND arr.year_cog = :year_cog
            
        """,
        {
            "geo_codes": geo_codes,
            "year_cog": SOURCE_OUTLINE,
        }
    )

    topography_arr = pd.DataFrame(result, columns=["geo_code", "outline", "arr_code", "arr_name"])
    topography_arr["outline"] = [shape(wkb_to_geojson(outline)) for outline in topography_arr["outline"]]
    topography_arr = topography_arr.groupby(by="arr_code", as_index=False).agg(**{
        "name": pd.NamedAgg(column="arr_name", aggfunc="first"),
        "outline": pd.NamedAgg(column="outline", aggfunc=lambda col: unary_union(col)),
    })
    topography_arr["center"] = [list(reversed(shape(outline).centroid.coords[0]))
                                for outline in topography_arr["outline"]]
    topography_arr["outline"] = [mapping(outline) for outline in topography_arr["outline"]]
    topography_arr = topography_arr.replace({np.nan: None})

    return {
        "arrondissements": topography_arr.to_dict(orient="list")
    }


def get_petr(geo_codes):
    result = db_request(
        """ SELECT petr.codgeo, ign_o.outline, petr.pays, petr.pays_libgeo
            FROM observatoire_petr AS petr
            LEFT JOIN ign_commune_outline AS ign_o ON petr.codgeo = ign_o.geo_code
            WHERE petr.pays IN (
                SELECT pays
                FROM observatoire_petr
                WHERE codgeo IN :geo_codes
                AND year_cog = :year_cog
              )
            AND petr.year_cog = :year_cog AND ign_o.year_cog = :year_cog
        """,
        {
            "geo_codes": geo_codes,
            "year_cog": SOURCE_OUTLINE,
        }
    )

    topography_petr = pd.DataFrame(result, columns=["geo_code", "outline", "petr_code", "petr_name"])
    topography_petr["outline"] = [shape(wkb_to_geojson(outline)) for outline in topography_petr["outline"]]
    topography_petr = topography_petr.groupby(by="petr_code", as_index=False).agg(**{
        "name": pd.NamedAgg(column="petr_name", aggfunc="first"),
        "outline": pd.NamedAgg(column="outline", aggfunc=lambda col: unary_union(col)),
    })
    topography_petr["center"] = [list(reversed(shape(outline).centroid.coords[0]))
                                 for outline in topography_petr["outline"]]
    topography_petr["outline"] = [mapping(outline) for outline in topography_petr["outline"]]
    topography_petr["name"] = [name.title() for name in topography_petr["name"]]
    topography_petr = topography_petr.replace({np.nan: None})

    return {
        "petrs": topography_petr.to_dict(orient="list"),
    }


def get_pnr(geo_codes):
    result = db_request(
        """ SELECT pnr.codgeo, ign_o.outline, pnr.pnr, pnr.pnr_libgeo
            FROM observatoire_pnr AS pnr
            LEFT JOIN ign_commune_outline AS ign_o ON pnr.codgeo = ign_o.geo_code
            WHERE pnr.pnr IN (
                SELECT pnr
                FROM observatoire_pnr
                WHERE codgeo IN :geo_codes
                AND year_data = :year_pnr
              )
            AND pnr.year_data = :year_pnr AND ign_o.year_cog = :year_cog
        """,
        {
            "geo_codes": geo_codes,
            "year_cog": SOURCE_OUTLINE,
            "year_pnr": SOURCE_PNR
        }
    )

    topography_pnr = pd.DataFrame(result, columns=["geo_code", "outline", "pnr_code", "pnr_name"])
    topography_pnr["outline"] = [shape(wkb_to_geojson(outline)) for outline in topography_pnr["outline"]]
    topography_pnr = topography_pnr.groupby(by="pnr_code", as_index=False).agg(**{
        "name": pd.NamedAgg(column="pnr_name", aggfunc="first"),
        "outline": pd.NamedAgg(column="outline", aggfunc=lambda col: unary_union(col)),
    })
    topography_pnr["center"] = [list(reversed(shape(outline).centroid.coords[0]))
                                for outline in topography_pnr["outline"]]
    topography_pnr["outline"] = [mapping(outline) for outline in topography_pnr["outline"]]
    topography_pnr = topography_pnr.replace({np.nan: None})

    return {
        "pnrs": topography_pnr.to_dict(orient="list"),
    }


def get_perimeters(geo_codes):
    result = db_request(
        """ SELECT epci_c.CODGEO, 
                          epci.EPCI, epci.LIBEPCI, 
                          arr.ARR, arr.LIBELLE,
                          aav_c.AAV, aav_c.CATEAAV, 
                          aav.LIBAAV, aav.TAAV,
                          petr.pays, petr.pays_libgeo,
                          pnr.pnr, pnr.pnr_libgeo,
                          zrr.zrr_type
            FROM insee_epci_communes AS epci_c
            JOIN insee_epci AS epci ON epci_c.EPCI = epci.EPCI

            JOIN insee_cog_communes AS cog_c ON cog_c.COM = epci_c.CODGEO
            JOIN insee_cog_arrondissements AS arr ON cog_c.ARR = arr.ARR

            JOIN observatoire_petr AS petr ON petr.codgeo = epci_c.CODGEO
            JOIN observatoire_pnr AS pnr ON pnr.codgeo = epci_c.CODGEO
            JOIN observatoire_zrr AS zrr ON zrr.CODGEO = epci_c.CODGEO

            JOIN insee_aav_communes AS aav_c ON aav_c.CODGEO = epci_c.CODGEO
            JOIN insee_aav AS aav ON aav.AAV = aav_c.AAV

            WHERE epci_c.CODGEO IN :geo_codes
            AND epci_c.year_data = :year_epci
            AND arr.year_data = :year_arr        
            AND aav.year_data = :year_aav
            AND petr.year_data = :year_petr
            AND pnr.year_data = :year_pnr
            AND zrr.year_data = :year_zrr
        """,
        {
            "geo_codes": geo_codes,
            "year_epci": SOURCE_EPCI,
            "year_arr": SOURCE_OUTLINE,
            "year_aav": "2020",
            "year_petr": SOURCE_PETR,
            "year_pnr": SOURCE_PNR,
            "year_zrr": SOURCE_ZRR
        }
    )
    perimeters = pd.DataFrame(result, columns=["geo_code",
                                               "epci_code", "epci_name",
                                               "arr_code", "arr_name",
                                               "aav_code", "aav_commune_cat",
                                               "aav_name", "aav_type",
                                               "petr_code", "petr_name",
                                               "pnr_code", "pnr_name",
                                               "zrr_type"
                                               ])
    perimeters = pd.merge(pd.DataFrame({"geo_code": geo_codes}), perimeters, on="geo_code", how="left")
    perimeters = perimeters.replace({np.nan: None})
    perimeters["petr_name"] = [name.title() if name is not None else "/" for name in perimeters["petr_name"]]
    perimeters["pnr_name"] = [name if name is not None else "/" for name in perimeters["pnr_name"]]
    perimeters["typo_aav"] = perimeters.apply(lambda row: str(row["aav_commune_cat"])[:1] + str(row["aav_type"]),
                                              axis=1)

    return {
        "com": perimeters.to_dict(orient="list"),
        "epci": None,
    }


class Arr(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("arr", geo_codes)
        return get_arrondissements(geo_codes)


class Petr(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("petr", geo_codes)
        return get_petr(geo_codes)


class Pnr(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("pnr", geo_codes)
        return get_pnr(geo_codes)


class Perimeters(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("perimeters", geo_codes)
        return get_perimeters(geo_codes)
