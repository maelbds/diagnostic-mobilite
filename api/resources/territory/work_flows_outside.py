import pandas as pd
import numpy as np
from pyproj import Transformer

from api.resources.common.cog import COG
from api.resources.common.log_stats import log_stats
from api.resources.common.utilities import wkb_to_geojson
from data_manager.sources.sources import get_years_for_source, get_label_link_for_source_year

from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request

from shapely import Point, distance
from shapely.geometry import shape

source_label = "insee_mobpro_flows_light"

dataset_work_flows_outside = {
    "endpoint": "territory/work_flows_outside",
    "is_mesh_element": False,
    "meshes": ["com", "epci"],
    "name_year": "INSEE MobPro",
    "years": get_years_for_source(source_label),
}


def compute_flows_distance(flows):
    # Lambert to Geodetic coordinates system :
    transformer = Transformer.from_crs("epsg:4326",  # World Geodetic System (lat/lon)
                                       "epsg:2154")  # Lambert

    def geo_to_lambert(lat, lon):
        x, y = transformer.transform(lat, lon)
        return [round(x), round(y)]

    def crow_fly_dist_to_real(dist_meters):
        dist_km = dist_meters / 1000
        # "From crow-fly distances to real distances, or the origin of detours, Heran"
        return round(dist_km * (1.1 + 0.3 * np.exp(-dist_km / 20)), 1)

    flows["home_coords"] = [geo_to_lambert(lat, lon) for lat, lon in zip(flows["home_lat"], flows["home_lon"])]
    flows["home_point"] = [Point(x, y) for x, y in flows["home_coords"]]
    flows["work_coords"] = [geo_to_lambert(lat, lon) for lat, lon in zip(flows["work_lat"], flows["work_lon"])]
    flows["work_point"] = [Point(x, y) for x, y in flows["work_coords"]]
    flows["distance"] = [crow_fly_dist_to_real(distance(p_home, p_work))
                         for p_home, p_work in zip(flows["home_point"], flows["work_point"])]

    flows.drop(columns=["home_coords", "home_point", "work_coords", "work_point"], inplace=True)
    return flows


def format_flows(flows):
    flows["flow"] = flows["flow"].round()
    flows = flows.replace({np.nan: None})
    return flows


def get_work_flows_outside(geo_codes, mesh, year):
    sources = [get_label_link_for_source_year(name, year) for name in [source_label]]

    flows = pd.DataFrame(data=None, columns=["home_geo_code", "home_lat", "home_lon", "home_name",
                                              "work_geo_code", "work_lat", "work_lon", "work_name",
                                              "distance", "flow"])

    if mesh == "com":
        result = db_request(
            """ SELECT  p1.CODGEO_DES, c1.chflieu_lat, c1.chflieu_lon, cog1.LIBELLE, 
                        p2.CODGEO_DES, c2.chflieu_lat, c2.chflieu_lon, cog2.LIBELLE, 
                        f.TRANS, f.flow
                FROM insee_mobpro_flows_light AS f
                
                LEFT JOIN insee_passage_cog AS p1 ON f.CODGEO_home = p1.CODGEO_INI
                LEFT JOIN ign_commune_center AS c1 ON p1.CODGEO_DES = c1.geo_code
                LEFT JOIN insee_cog_communes AS cog1 ON p1.CODGEO_DES = cog1.COM
                
                LEFT JOIN insee_passage_cog AS p2 ON f.CODGEO_work = p2.CODGEO_INI
                LEFT JOIN ign_commune_center AS c2 ON p2.CODGEO_DES = c2.geo_code
                LEFT JOIN insee_cog_communes AS cog2 ON p2.CODGEO_DES = cog2.COM
                
                WHERE p2.CODGEO_DES IN :geo_codes
                AND p1.CODGEO_DES NOT IN :geo_codes
                AND f.year_data = :year_mobpro
                
                AND c1.year_cog = :cog
                AND cog1.year_cog = :cog
                AND c2.year_cog = :cog
                AND cog2.year_cog = :cog
            """,
            {
                "geo_codes": geo_codes,
                "year_mobpro": year,
                "cog": COG
            }
        )

        flows = pd.DataFrame(result, columns=["home_geo_code", "home_lat", "home_lon", "home_name",
                                              "work_geo_code", "work_lat", "work_lon", "work_name",
                                              "mode", "flow"])

        mask_typmr_1 = flows["mode"] == "1"
        flows.loc[mask_typmr_1, "work_geo_code"] = flows.loc[mask_typmr_1, "home_geo_code"]
        flows.loc[mask_typmr_1, "work_lat"] = flows.loc[mask_typmr_1, "home_lat"]
        flows.loc[mask_typmr_1, "work_lon"] = flows.loc[mask_typmr_1, "home_lon"]
        flows.loc[mask_typmr_1, "work_name"] = flows.loc[mask_typmr_1, "home_name"]

        flows = flows.groupby(by=[e for e in flows.columns if e != "flow" and e != "mode"], as_index=False).sum()
        flows = compute_flows_distance(flows)
        flows = format_flows(flows)

    elif mesh == "epci":
        result = db_request(
            """ SELECT epci1.EPCI, epci2.EPCI, f.flow
                FROM insee_mobpro_flows_light AS f
                
                LEFT JOIN insee_passage_cog AS p1 ON f.CODGEO_home = p1.CODGEO_INI
                LEFT JOIN insee_epci_communes AS epci1 ON p1.CODGEO_DES = epci1.CODGEO
                
                LEFT JOIN insee_passage_cog AS p2 ON f.CODGEO_work = p2.CODGEO_INI
                LEFT JOIN insee_epci_communes AS epci2 ON p2.CODGEO_DES = epci2.CODGEO
                
                WHERE epci2.EPCI IN (
                    SELECT epci.EPCI
                    FROM insee_epci_communes AS epci
                    WHERE epci.CODGEO IN :geo_codes 
                    AND epci.year_cog = :cog
                  ) 
                AND epci1.EPCI NOT IN (
                    SELECT epci.EPCI
                    FROM insee_epci_communes AS epci
                    WHERE epci.CODGEO IN :geo_codes 
                    AND epci.year_cog = :cog
                  ) 
                AND f.year_data = :year_mobpro
                
                AND p1.year_cog = :cog
                AND epci1.year_cog = :cog
                AND p2.year_cog = :cog
                AND epci2.year_cog = :cog
            """,
            {
                "geo_codes": geo_codes,
                "year_mobpro": year,
                "cog": COG
            }
        )
        flows = pd.DataFrame(result, columns=["home_geo_code",
                                              "work_geo_code",
                                              "flow"])

        # get epcis names and center
        result = db_request(
            """ SELECT epci.EPCI, epci.LIBEPCI, ign_epci.outline
            
                FROM insee_epci AS epci
                LEFT JOIN ign_epci_outline AS ign_epci ON epci.EPCI = ign_epci.epci_siren
                
                WHERE epci.EPCI in :epcis
                AND epci.year_cog = :cog
                AND ign_epci.year_cog = :cog
            """,
            {
                "epcis": flows["home_geo_code"].drop_duplicates().to_list() +
                         flows["work_geo_code"].drop_duplicates().to_list(),
                "cog": COG,
            }
        )
        epcis = pd.DataFrame(result, columns=["code", "name", "outline"]).dropna()

        epcis["outline"] = [wkb_to_geojson(outline) for outline in epcis["outline"]]
        epcis["center"] = [list(reversed(shape(outline).centroid.coords[0])) for outline in epcis["outline"]]
        epcis.drop(columns=["outline"], inplace=True)
        epcis.dropna(inplace=True)

        flows = pd.merge(flows, epcis, left_on="home_geo_code", right_on="code", how="inner")
        flows = pd.merge(flows, epcis, left_on="work_geo_code", right_on="code", how="inner", suffixes=(None, "_work"))

        flows.drop(columns=["code", "code_work"], inplace=True)
        flows.rename(columns={
            "center": "home_center", "name": "home_name",
            "center_work": "work_center", "name_work": "work_name"
        }, inplace=True)

        flows["home_lat"] = [c[0] for c in flows["home_center"]]
        flows["home_lon"] = [c[1] for c in flows["home_center"]]
        flows["work_lat"] = [c[0] for c in flows["work_center"]]
        flows["work_lon"] = [c[1] for c in flows["work_center"]]
        flows.drop(columns=["home_center", "work_center"], inplace=True)

        flows = flows.groupby(by=[e for e in flows.columns if e != "flow"], as_index=False).sum()
        flows = compute_flows_distance(flows)
        flows = format_flows(flows)

    return {
        "elements": {
            "work_flows": {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {
                    "home_name": home_name,
                    "home_geo_code": home_geo_code,
                    "work_name": work_name,
                    "work_geo_code": work_geo_code,
                    "flow": flow,
                    "distance": distance,
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[home_lon, home_lat], [work_lon, work_lat]]
                }
            } for home_geo_code, home_lat, home_lon, home_name,
                  work_geo_code, work_lat, work_lon, work_name,
                  flow, distance in zip(
                flows["home_geo_code"], flows["home_lat"], flows["home_lon"], flows["home_name"],
                flows["work_geo_code"], flows["work_lat"], flows["work_lon"], flows["work_name"],
                flows["flow"],
                flows["distance"]
            )]
        }},
        "sources": sources,
        "is_mesh_element": False
    }


class WorkFlowsOutside(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes
        year = perimeter.year
        mesh = perimeter.mesh

        log_stats("work_flows_outside", geo_codes, mesh, year)
        message_request("work_flows_outside", geo_codes)
        return get_work_flows_outside(geo_codes, mesh, year)


if __name__ == '__main__':
    print(get_work_flows_outside(["79048"], "epci", "2018"))

