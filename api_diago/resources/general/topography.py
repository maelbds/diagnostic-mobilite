import pandas as pd
import numpy as np
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

from data_manager.ign.source import SOURCE_OUTLINE

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request
from api_diago.resources.common.utilities import wkb_to_geojson


def select_names_to_display(topography_communes):
    approx_deg_km = np.array([np.pi / 180 * 6400, np.pi / 180 * 4400])
    def distance(c1, c2):
        X = np.array(c1)
        Y = np.array(c2)
        return abs(np.linalg.norm(np.multiply(X - Y, approx_deg_km)))

    lat = [c[0] for c in topography_communes["center"]]
    lon = [c[1] for c in topography_communes["center"]]

    min_all = [min(lat), min(lon)]
    max_all = [max(lat), max(lon)]
    caracteristic_dist = distance(min_all, max_all) / 8

    topography_communes = topography_communes.sort_values(by=["population"], ascending=False)
    display_name = []

    [display_name.append(
        all([
            distance(c_center, c) > caracteristic_dist for c in topography_communes["center"].iloc[:i][display_name]
        ])
    ) for c_pop, c_center, i
      in zip(topography_communes["population"], topography_communes["center"], range(len(topography_communes)))]

    topography_communes["display_name"] = display_name

    return topography_communes[["geo_code", "display_name"]]


def get_topography(geo_codes):
    result = db_request(
        """ SELECT cog.COM, cog.LIBELLE, epci.EPCI, pop.POP, 
                  ign_c.centroid_lat, ign_c.centroid_lon, 
                  ign_c.chflieu_lat, ign_c.chflieu_lon,
                  ign_o.outline
            FROM insee_cog_communes AS cog
            LEFT JOIN insee_dossier_complet_mobin AS pop ON cog.COM = pop.CODGEO
            LEFT JOIN ign_commune_center AS ign_c ON cog.COM = ign_c.geo_code
            LEFT JOIN ign_commune_outline AS ign_o ON cog.COM = ign_o.geo_code
            LEFT JOIN insee_epci_communes AS epci ON cog.COM = epci.CODGEO
            WHERE cog.COM IN :geo_codes
            AND ign_o.year_data = :year_data AND ign_o.year_cog = :year_cog""",
        {
            "geo_codes": geo_codes,
            "year_data": SOURCE_OUTLINE,
            "year_cog": SOURCE_OUTLINE
        }
    )

    topography_communes = pd.DataFrame(result, columns=["geo_code", "name", "epci", "population",
                                                        "centroid_lat", "centroid_lon", "chflieu_lat",
                                                        "chflieu_lon",
                                                        "outline"])
    topography_communes = topography_communes.replace({np.nan: None})
    topography_communes["center"] = topography_communes.apply(
        lambda row: [row["centroid_lat"], row["centroid_lon"]] if row["chflieu_lat"] is None else
        [row["chflieu_lat"], row["chflieu_lon"]], axis=1
    )
    topography_communes = topography_communes.drop(
        columns=["centroid_lat", "centroid_lon", "chflieu_lat", "chflieu_lon"])
    topography_communes["outline"] = [wkb_to_geojson(outline) for outline in topography_communes["outline"]]
    topography_communes["name"] = [name.replace("Saint", "St") for name in topography_communes["name"]]
    topography_communes = topography_communes.fillna(0)
    topography_communes = topography_communes.replace({np.nan: None})

    display_name = select_names_to_display(topography_communes)
    topography_communes = pd.merge(topography_communes, display_name, on="geo_code")
    topography_communes = pd.merge(pd.DataFrame({"geo_code": geo_codes}), topography_communes, on="geo_code", how="left")

    # EPCI
    epci_codes = sorted([g for g in topography_communes["epci"].drop_duplicates() if g != "ZZZZZZZZZ"])

    result = db_request(
        """ SELECT epci.EPCI, epci.LIBEPCI, ign.outline
            FROM insee_epci AS epci
            LEFT JOIN ign_epci_outline AS ign ON epci.EPCI = ign.epci_siren
            WHERE epci.EPCI IN :geo_codes 
            AND epci.year_data = :year_data_epci AND ign.year_data = :year_data_ign""",
        {
            "geo_codes": epci_codes,
            "year_data_epci": SOURCE_OUTLINE,
            "year_data_ign": SOURCE_OUTLINE
        }
    )

    topography_epci = pd.DataFrame(result, columns=["geo_code", "name", "outline"])
    topography_epci["outline"] = [wkb_to_geojson(outline) for outline in topography_epci["outline"]]
    topography_epci["center"] = [list(reversed(shape(outline).centroid.coords[0])) for outline in topography_epci["outline"]]
    topography_epci = pd.merge(pd.DataFrame({"geo_code": epci_codes}), topography_epci, on="geo_code", how="left")
    topography_epci = topography_epci.replace({np.nan: None})
    topography_epci["display_name"] = True
    topography_epci = pd.merge(topography_epci, topography_communes[["epci", "population"]].groupby("epci").sum(),
                              left_on="geo_code", right_index=True, how="left")

    # perimeter
    commune_outlines = topography_communes["outline"].to_list()
    commune_outlines_shapes = [shape(o) for o in commune_outlines]
    perimeter = mapping(unary_union(commune_outlines_shapes))

    return {
        "com": topography_communes.to_dict(orient="list"),
        "epci": topography_epci.to_dict(orient="list"),
        "perimeter": perimeter
    }


class Topography(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("topography", geo_codes)
        return get_topography(geo_codes)

