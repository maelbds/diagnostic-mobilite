import pandas as pd
import numpy as np

from api.resources.common.cog import COG

from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.log_stats import log_stats
from api.resources.common.schema_request import context_get_request


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


def get_geography(geo_codes):
    result = db_request(
        """ SELECT cog.COM, cog.LIBELLE, 
                  epci.EPCI, 
                  pop.POP, 
                  ign_c.centroid_lat, ign_c.centroid_lon, 
                  ign_c.chflieu_lat, ign_c.chflieu_lon
            FROM insee_cog_communes AS cog
            LEFT JOIN insee_dossier_complet AS pop ON cog.COM = pop.CODGEO
            LEFT JOIN ign_commune_center AS ign_c ON cog.COM = ign_c.geo_code
            LEFT JOIN insee_epci_communes AS epci ON cog.COM = epci.CODGEO
            WHERE cog.COM IN :geo_codes
            AND cog.year_cog = :cog
            AND pop.year_data = :year_data
            AND ign_c.year_cog = :cog
            AND epci.year_cog = :cog
            """,
        {
            "geo_codes": geo_codes,
            "year_data": "2020",
            "cog": COG,
        }
    )

    geography_communes = pd.DataFrame(result, columns=["geo_code", "name", "epci", "population",
                                                        "centroid_lat", "centroid_lon",
                                                        "chflieu_lat", "chflieu_lon"])
    geography_communes = geography_communes.replace({np.nan: None})
    geography_communes["center"] = geography_communes.apply(
        lambda row: [row["centroid_lon"], row["centroid_lat"]] if row["chflieu_lat"] is None else
        [row["chflieu_lon"], row["chflieu_lat"]], axis=1
    )
    geography_communes = geography_communes.drop(
        columns=["centroid_lat", "centroid_lon", "chflieu_lat", "chflieu_lon"])
    #topography_communes["outline"] = [wkb_to_geojson(outline) for outline in topography_communes["outline"]]
    geography_communes["name"] = [name.replace("Saint", "St") for name in geography_communes["name"]]
    geography_communes = geography_communes.fillna(0)
    geography_communes = geography_communes.replace({np.nan: None})

    # display_name = select_names_to_display(topography_communes)
    # topography_communes = pd.merge(topography_communes, display_name, on="geo_code")
    geography_communes = pd.merge(pd.DataFrame({"geo_code": geo_codes}), geography_communes, on="geo_code", how="left")

    # EPCI
    epci_codes = sorted([g for g in geography_communes["epci"].drop_duplicates() if g != "ZZZZZZZZZ"])

    result = db_request(
        """ SELECT epci.EPCI, epci.LIBEPCI
            FROM insee_epci AS epci
            WHERE epci.EPCI IN :geo_codes 
            AND epci.year_cog = :cog
            """,
        {
            "geo_codes": epci_codes,
            "cog": COG
        }
    )

    geography_epci = pd.DataFrame(result, columns=["geo_code", "name"])
    geography_epci = pd.merge(pd.DataFrame({"geo_code": epci_codes}), geography_epci, on="geo_code", how="left")
    geography_epci = geography_epci.replace({np.nan: None})

    return {
        "com": geography_communes.to_dict(orient="records"),
        "epci": geography_epci.to_dict(orient="records")
    }


class Geography(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes

        log_stats("geography", geo_codes, None, None)
        message_request("geography", geo_codes)
        return get_geography(geo_codes)


if __name__ == '__main__':
    print(get_geography(["79023","79042","79201","79246","79303","79316","79020","79024","79048","79086","79128",
                         "79231","79276","79283","79302","79319","79114","79189","79270"]))


"""

attention : wkb_to_geojson return geom_collection
topography_communes = gpd.GeoDataFrame(topography_communes, geometry="outline")
json.loads(topography_communes.to_json())

"""
