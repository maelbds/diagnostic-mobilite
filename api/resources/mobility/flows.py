import pandas as pd
import numpy as np

from api.resources.common.cog import COG
from api.resources.common.log_stats import log_stats
from api.resources.common.utilities import wkb_to_geojson
from api.resources.mobility.utilities.get_travels_sources import get_travels_sources
from api.resources.mobility.utilities.get_travels_situation import get_travels_situation

from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request

from shapely.geometry import shape

from api.resources.mobility.utilities.significance_threshold import SIGNIFICANCE_THRESHOLD

dataset_flows = {
    "endpoint": "mobility/flows",
    "is_mesh_element": False,
    "meshes": ["com", "epci"],
    "name_year": "Modélisation",
    "years": ["2018"],
}


def format_flows(flows):
    flows["distance"] = flows["distance"] * flows["number"]

    geo_columns = ["ori_geo_code", "ori_lat", "ori_lon", "ori_name",
                   "des_geo_code", "des_lat", "des_lon", "des_name"]

    # A->B & B->A to A<->B
    mask_swap = flows["ori_geo_code"] > flows["des_geo_code"]

    for col_name in ["geo_code", "lat", "lon", "name"]:
        flows.loc[mask_swap, "swap_" + col_name] = flows.loc[mask_swap, "ori_" + col_name]
        flows.loc[mask_swap, "ori_" + col_name] = flows.loc[mask_swap, "des_" + col_name]
        flows.loc[mask_swap, "des_" + col_name] = flows.loc[mask_swap, "swap_" + col_name]

    flows.drop(columns=["swap_" + c for c in ["geo_code", "lat", "lon", "name"]], inplace=True)

    # group flows by ori des pair
    flows = flows.groupby(geo_columns, as_index=False).agg(**{
        "distance": pd.NamedAgg(column="distance", aggfunc="sum"),
        "number": pd.NamedAgg(column="number", aggfunc="sum"),
        "sample": pd.NamedAgg(column="id_ind", aggfunc=lambda x: x.drop_duplicates().count()),
    })

    flows["number"] = flows["number"].round()
    flows["distance"] = flows["distance"].round()
    flows = flows.replace({np.nan: None})
    return flows


def get_flows(geo_codes, mesh, year):
    flows = pd.DataFrame(data=None, columns=["home_geo_code", "home_lat", "home_lon", "home_name",
                                             "des_geo_code", "des_lat", "des_lon", "des_name",
                                             "distance", "flow"])
    travels_situation = get_travels_situation(geo_codes)

    if mesh == "com":
        flows_cols = ["ori_geo_code", "ori_lat", "ori_lon", "ori_name",
                      "des_geo_code", "des_lat", "des_lon", "des_name",
                      "distance", "number", "id_ind"]
        flows = pd.DataFrame(None, columns=flows_cols)

        if travels_situation == "model":
            result = db_request(
                """ SELECT  p1.CODGEO_DES, c1.chflieu_lat, c1.chflieu_lon, cog1.LIBELLE, 
                            p2.CODGEO_DES, c2.chflieu_lat, c2.chflieu_lon, cog2.LIBELLE, 
                            ct.distance,
                            ct.w_trav,
                            ct.id_ind
    
                    FROM computed_travels AS ct
                    
                    LEFT JOIN insee_passage_cog AS p0 ON ct.geo_code = p0.CODGEO_INI
                    
                    LEFT JOIN insee_passage_cog AS p1 ON ct.geo_code_ori = p1.CODGEO_INI
                    LEFT JOIN ign_commune_center AS c1 ON p1.CODGEO_DES = c1.geo_code
                    LEFT JOIN insee_cog_communes AS cog1 ON p1.CODGEO_DES = cog1.COM
                    
                    LEFT JOIN insee_passage_cog AS p2 ON ct.geo_code_des = p2.CODGEO_INI
                    LEFT JOIN ign_commune_center AS c2 ON p2.CODGEO_DES = c2.geo_code
                    LEFT JOIN insee_cog_communes AS cog2 ON p2.CODGEO_DES = cog2.COM
    
                    WHERE p0.CODGEO_DES IN :geo_codes
                    
                    AND p0.year_cog = :cog
                    AND p1.year_cog = :cog
                    AND p2.year_cog = :cog
                    AND c1.year_cog = :cog
                    AND cog1.year_cog = :cog
                    AND c2.year_cog = :cog
                    AND cog2.year_cog = :cog
                    
                    """,
                {
                    "geo_codes": geo_codes,
                    "cog": COG
                })

            flows = pd.DataFrame(result, columns=flows_cols)

        if travels_situation == "emd":
            result = db_request(
                """ SELECT  p1.CODGEO_DES, c1.chflieu_lat, c1.chflieu_lon, cog1.LIBELLE, 
                            p2.CODGEO_DES, c2.chflieu_lat, c2.chflieu_lon, cog2.LIBELLE, 
                            t.distance,
                            p.w_ind,
                            t.id_ind

                    FROM emd_travels AS t
                    JOIN emd_persons AS p ON t.id_ind = p.id_ind AND t.emd_id = p.emd_id
                    JOIN emd_mobloc AS m ON t.emd_id = m.emd_id AND t.id_trav = m.id_trav
                    
                    LEFT JOIN emd_geo AS emd_geo_ori ON t.zone_ori = emd_geo_ori.id AND t.emd_id = emd_geo_ori.emd_id
                    LEFT JOIN insee_arrondissements_passage AS arr1 ON emd_geo_ori.geo_code = arr1.geo_code_district
                    LEFT JOIN insee_passage_cog AS p1 ON arr1.geo_code_city = p1.CODGEO_INI
                    LEFT JOIN ign_commune_center AS c1 ON p1.CODGEO_DES = c1.geo_code
                    LEFT JOIN insee_cog_communes AS cog1 ON p1.CODGEO_DES = cog1.COM
                   
                    LEFT JOIN emd_geo AS emd_geo_des ON t.zone_des = emd_geo_des.id AND t.emd_id = emd_geo_des.emd_id
                    LEFT JOIN insee_arrondissements_passage AS arr2 ON emd_geo_des.geo_code = arr2.geo_code_district
                    LEFT JOIN insee_passage_cog AS p2 ON arr2.geo_code_city = p2.CODGEO_INI
                    LEFT JOIN ign_commune_center AS c2 ON p2.CODGEO_DES = c2.geo_code
                    LEFT JOIN insee_cog_communes AS cog2 ON p2.CODGEO_DES = cog2.COM
                   
                    LEFT JOIN emd_geo AS emd_geo_res ON t.ra_id = emd_geo_res.id AND t.emd_id = emd_geo_res.emd_id
                    LEFT JOIN insee_arrondissements_passage AS arr0 ON emd_geo_res.geo_code = arr0.geo_code_district
                    LEFT JOIN insee_passage_cog AS p0 ON arr0.geo_code_city = p0.CODGEO_INI
                   
                    WHERE p0.CODGEO_DES IN :geo_codes
                    AND p.age > 5
                    AND p.day < 6
                    AND m.mobloc = 1

                    AND arr0.year_cog = :cog
                    AND arr1.year_cog = :cog
                    AND arr2.year_cog = :cog
                    AND p0.year_cog = :cog
                    AND p1.year_cog = :cog
                    AND p2.year_cog = :cog
                    AND c1.year_cog = :cog
                    AND cog1.year_cog = :cog
                    AND c2.year_cog = :cog
                    AND cog2.year_cog = :cog

                    """,
                {
                    "geo_codes": geo_codes,
                    "cog": COG
                })

            flows = pd.DataFrame(result, columns=flows_cols)
            flows["distance"] = flows["distance"].astype(float)

        flows = format_flows(flows)

    elif mesh == "epci":
        flows_cols = ["ori_geo_code", "des_geo_code", "distance", "number", "id_ind"]
        flows = pd.DataFrame(None, columns=flows_cols)

        if travels_situation == "model":
            result = db_request(
                """ SELECT  epci1.EPCI, 
                            epci2.EPCI,
                            ct.distance,
                            ct.w_trav,
                            ct.id_ind
    
                    FROM computed_travels AS ct
                    
                    LEFT JOIN insee_passage_cog AS p0 ON ct.geo_code = p0.CODGEO_INI
                    LEFT JOIN insee_epci_communes AS epci0 ON p0.CODGEO_DES = epci0.CODGEO
                    
                    LEFT JOIN insee_passage_cog AS p1 ON ct.geo_code_ori = p1.CODGEO_INI
                    LEFT JOIN insee_epci_communes AS epci1 ON p1.CODGEO_DES = epci1.CODGEO
                    
                    LEFT JOIN insee_passage_cog AS p2 ON ct.geo_code_des = p2.CODGEO_INI
                    LEFT JOIN insee_epci_communes AS epci2 ON p2.CODGEO_DES = epci2.CODGEO
    
                    WHERE epci0.EPCI IN (
                        SELECT epci.EPCI
                        FROM insee_epci_communes AS epci
                        WHERE epci.CODGEO IN :geo_codes 
                        AND epci.year_cog = :cog
                      ) 
                    
                    AND p0.year_cog = :cog
                    AND p1.year_cog = :cog
                    AND p2.year_cog = :cog
                    
                    AND epci0.year_cog = :cog
                    AND epci1.year_cog = :cog
                    AND epci2.year_cog = :cog
                """,
                {
                    "geo_codes": geo_codes,
                    "cog": COG
                }
            )
            flows = pd.DataFrame(result, columns=flows_cols)

        if travels_situation == "emd":
            result = db_request(
                """ SELECT  epci1.EPCI, 
                            epci2.EPCI,
                            t.distance,
                            p.w_ind,
                            t.id_ind

                    FROM emd_travels AS t
                    JOIN emd_persons AS p ON t.id_ind = p.id_ind AND t.emd_id = p.emd_id
                    JOIN emd_mobloc AS m ON t.emd_id = m.emd_id AND t.id_trav = m.id_trav

                    LEFT JOIN emd_geo AS emd_geo_ori ON t.zone_ori = emd_geo_ori.id AND t.emd_id = emd_geo_ori.emd_id
                    LEFT JOIN insee_arrondissements_passage AS arr1 ON emd_geo_ori.geo_code = arr1.geo_code_district
                    LEFT JOIN insee_passage_cog AS p1 ON arr1.geo_code_city = p1.CODGEO_INI
                    LEFT JOIN insee_epci_communes AS epci1 ON p1.CODGEO_DES = epci1.CODGEO

                    LEFT JOIN emd_geo AS emd_geo_des ON t.zone_des = emd_geo_des.id AND t.emd_id = emd_geo_des.emd_id
                    LEFT JOIN insee_arrondissements_passage AS arr2 ON emd_geo_des.geo_code = arr2.geo_code_district
                    LEFT JOIN insee_passage_cog AS p2 ON arr2.geo_code_city = p2.CODGEO_INI
                    LEFT JOIN insee_epci_communes AS epci2 ON p2.CODGEO_DES = epci2.CODGEO

                    LEFT JOIN emd_geo AS emd_geo_res ON t.ra_id = emd_geo_res.id AND t.emd_id = emd_geo_res.emd_id
                    LEFT JOIN insee_arrondissements_passage AS arr0 ON emd_geo_res.geo_code = arr0.geo_code_district
                    LEFT JOIN insee_passage_cog AS p0 ON arr0.geo_code_city = p0.CODGEO_INI
                    LEFT JOIN insee_epci_communes AS epci0 ON p0.CODGEO_DES = epci0.CODGEO

                    WHERE epci0.EPCI IN (
                        SELECT epci.EPCI
                        FROM insee_epci_communes AS epci
                        WHERE epci.CODGEO IN :geo_codes 
                        AND epci.year_cog = :cog
                      ) 
                    AND m.mobloc = 1
                    
                    AND p0.year_cog = :cog
                    AND p1.year_cog = :cog
                    AND p2.year_cog = :cog
                    AND arr0.year_cog = :cog
                    AND arr1.year_cog = :cog
                    AND arr2.year_cog = :cog
                    
                    AND epci0.year_cog = :cog
                    AND epci1.year_cog = :cog
                    AND epci2.year_cog = :cog
                    """,
                {
                    "geo_codes": geo_codes,
                    "cog": COG
                })

            flows = pd.DataFrame(result, columns=flows_cols)
            flows["distance"] = flows["distance"].astype(float)

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
                "epcis": flows["ori_geo_code"].drop_duplicates().to_list() +
                         flows["des_geo_code"].drop_duplicates().to_list(),
                "cog": COG,
            }
        )
        epcis = pd.DataFrame(result, columns=["code", "name", "outline"]).dropna()

        epcis["outline"] = [wkb_to_geojson(outline) for outline in epcis["outline"]]
        epcis["center"] = [list(reversed(shape(outline).centroid.coords[0])) for outline in epcis["outline"]]
        epcis.drop(columns=["outline"], inplace=True)
        epcis.dropna(inplace=True)

        flows = pd.merge(flows, epcis, left_on="ori_geo_code", right_on="code", how="inner")
        flows = pd.merge(flows, epcis, left_on="des_geo_code", right_on="code", how="inner", suffixes=(None, "_des"))

        flows.drop(columns=["code", "code_des"], inplace=True)
        flows.rename(columns={
            "center": "ori_center", "name": "ori_name",
            "center_des": "des_center", "name_des": "des_name"
        }, inplace=True)

        flows["ori_lat"] = [c[0] for c in flows["ori_center"]]
        flows["ori_lon"] = [c[1] for c in flows["ori_center"]]
        flows["des_lat"] = [c[0] for c in flows["des_center"]]
        flows["des_lon"] = [c[1] for c in flows["des_center"]]
        flows.drop(columns=["ori_center", "des_center"], inplace=True)

        flows = format_flows(flows)

    flows["prop_distance"] = (flows["distance"] / flows["distance"].sum() * 100).round(1)
    flows["prop_number"] = (flows["number"] / flows["number"].sum() * 100).round(1)

    mask_significance = flows["sample"] >= SIGNIFICANCE_THRESHOLD
    flows = flows.loc[mask_significance]

    return {
        "elements": {
            "flows": {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {
                        "ori_name": ori_name,
                        "ori_geo_code": ori_geo_code,
                        "des_name": des_name,
                        "des_geo_code": des_geo_code,
                        "number": number,
                        "prop_number": prop_number,
                        "distance": distance,
                        "prop_distance": prop_distance,
                        "sample": sample,
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[ori_lon, ori_lat], [des_lon, des_lat]]
                    }
                } for ori_geo_code, ori_lat, ori_lon, ori_name,
                      des_geo_code, des_lat, des_lon, des_name,
                      number, distance, prop_number, prop_distance, sample in zip(
                    flows["ori_geo_code"], flows["ori_lat"], flows["ori_lon"], flows["ori_name"],
                    flows["des_geo_code"], flows["des_lat"], flows["des_lon"], flows["des_name"],
                    flows["number"],
                    flows["distance"],
                    flows["prop_number"],
                    flows["prop_distance"],
                    flows["sample"],
                )]
            }},
        "sources": get_travels_sources(geo_codes),
        "is_mesh_element": False
    }


class Flows(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes
        year = perimeter.year
        mesh = perimeter.mesh

        log_stats("flows", geo_codes, mesh, year)
        message_request("flows", geo_codes)
        return get_flows(geo_codes, mesh, year)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)
    print(get_flows(["69123"], "epci", "2018"))

