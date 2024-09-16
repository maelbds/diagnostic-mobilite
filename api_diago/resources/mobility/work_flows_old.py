import pandas as pd
import numpy as np
from shapely.geometry import shape
from pyproj import Transformer
from shapely import Point, distance
import requests

from data_manager.insee_general.source import SOURCE_EPCI

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request
from api_diago.resources.common.utilities import wkb_to_geojson


def get_work_flows(geo_codes):
    result = db_request(
        """ SELECT  f.CODGEO_home, c1.chflieu_lat, c1.chflieu_lon, cog1.LIBELLE, 
                    f.CODGEO_work, c2.chflieu_lat, c2.chflieu_lon, cog2.LIBELLE, 
                    f.TRANS, f.SEXE, f.CS1, f.TYPMR, f.flow
            FROM insee_flows_mobpro AS f
            LEFT JOIN ign_commune_center AS c1 ON f.CODGEO_home = c1.geo_code
            LEFT JOIN insee_cog_communes AS cog1 ON f.CODGEO_home = cog1.COM
            LEFT JOIN ign_commune_center AS c2 ON f.CODGEO_work = c2.geo_code
            LEFT JOIN insee_cog_communes AS cog2 ON f.CODGEO_work = cog2.COM
            WHERE f.CODGEO_home IN :geo_codes
            AND f.year_data = :year_mobpro
        """,
        {
            "geo_codes": geo_codes,
            "year_mobpro": "2018",
        }
    )

    flows = pd.DataFrame(result, columns=["home_geo_code", "home_lat", "home_lon", "home_name",
                                          "work_geo_code", "work_lat", "work_lon", "work_name",
                                          "mode", "gender", "csp", "typmr", "flow"])
    mask_typmr_1 = flows["mode"] == "1"
    flows.loc[mask_typmr_1, "work_geo_code"] = flows.loc[mask_typmr_1, "home_geo_code"]
    flows.loc[mask_typmr_1, "work_lat"] = flows.loc[mask_typmr_1, "home_lat"]
    flows.loc[mask_typmr_1, "work_lon"] = flows.loc[mask_typmr_1, "home_lon"]
    flows.loc[mask_typmr_1, "work_name"] = flows.loc[mask_typmr_1, "home_name"]

    flows = flows.groupby(by=[e for e in flows.columns if e != "flow"], as_index=False).sum()

    # Lambert to Geodetic coordinates system :
    transformer = Transformer.from_crs("epsg:4326",  # World Geodetic System (lat/lon)
                                       "epsg:2154")  # Lambert

    def geo_to_lambert(lat, lon):
        x, y = transformer.transform(lat, lon)
        return [round(x), round(y)]

    def crow_fly_dist_to_real(dist_meters):
        dist_km = dist_meters / 1000
        # "From crow-fly distances to real distances, or the origin of detours, Heran"
        return dist_km * (1.1 + 0.3 * np.exp(-dist_km / 20))

    flows["home_coords"] = [geo_to_lambert(lat, lon) for lat, lon in zip(flows["home_lat"], flows["home_lon"])]
    flows["home_point"] = [Point(x, y) for x, y in flows["home_coords"]]
    flows["work_coords"] = [geo_to_lambert(lat, lon) for lat, lon in zip(flows["work_lat"], flows["work_lon"])]
    flows["work_point"] = [Point(x, y) for x, y in flows["work_coords"]]
    flows["distance"] = [crow_fly_dist_to_real(distance(p_home, p_work))
                         for p_home, p_work in zip(flows["home_point"], flows["work_point"])]

    flows.drop(columns=["home_coords", "home_point", "work_coords", "work_point"], inplace=True)

    flows = flows.replace({np.nan: None})

    flows["gender"] = flows["gender"].replace({"1": "m", "2": "f"})
    flows["typmr"] = flows["typmr"].replace({
        "11": "1",
        "12": "1",
        "31": "2",
        "32": "2",
        "42": "3",
        "43": "3",
        "41": "4",
        "ZZ": "5",
        "20": "5",
        "44": "5",
    })

    flows["mesh"] = "com"
    flows_com = flows

    # ---------- EPCI
    result = db_request(
        """ SELECT  epci_h.EPCI, 
                    epci_w.EPCI, 
                    f.TRANS, f.SEXE, f.CS1, f.TYPMR, f.flow
            FROM insee_flows_mobpro AS f
            LEFT JOIN insee_epci_communes AS epci_h ON f.CODGEO_home = epci_h.CODGEO
            LEFT JOIN insee_epci_communes AS epci_w ON f.CODGEO_work = epci_w.CODGEO
            WHERE epci_h.EPCI IN (
                SELECT epci2.EPCI
                FROM insee_epci_communes AS epci2
                WHERE epci2.CODGEO IN :geo_codes 
                AND epci2.year_data = :year_epci
              ) 
            AND f.year_data = :year_mobpro
        """,
        {
            "geo_codes": geo_codes,
            "year_mobpro": "2018",
            "year_epci": SOURCE_EPCI
        }
    )
    flows = pd.DataFrame(result, columns=["home_geo_code",
                                          "work_geo_code",
                                          "mode", "gender", "csp", "typmr", "flow"])

    result = db_request(
        """ SELECT epci.EPCI, epci.LIBEPCI, ign_epci.outline
            FROM insee_epci AS epci
            LEFT JOIN ign_epci_outline AS ign_epci ON epci.EPCI = ign_epci.epci_siren
        """,
        {}
    )
    epcis = pd.DataFrame(result, columns=["code",
                                          "name",
                                          "outline"]).dropna()

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

    # Lambert to Geodetic coordinates system :
    transformer = Transformer.from_crs("epsg:4326",  # World Geodetic System (lat/lon)
                                       "epsg:2154")  # Lambert

    def geo_to_lambert(lat, lon):
        x, y = transformer.transform(lat, lon)
        return [round(x), round(y)]

    def crow_fly_dist_to_real(dist_meters):
        dist_km = dist_meters / 1000
        # "From crow-fly distances to real distances, or the origin of detours, Heran"
        return dist_km * (1.1 + 0.3 * np.exp(-dist_km / 20))

    flows["home_coords"] = [geo_to_lambert(lat, lon) for lat, lon in zip(flows["home_lat"], flows["home_lon"])]
    flows["home_point"] = [Point(x, y) for x, y in flows["home_coords"]]
    flows["work_coords"] = [geo_to_lambert(lat, lon) for lat, lon in zip(flows["work_lat"], flows["work_lon"])]
    flows["work_point"] = [Point(x, y) for x, y in flows["work_coords"]]

    flows["distance"] = [crow_fly_dist_to_real(distance(p_home, p_work))
                         for p_home, p_work in zip(flows["home_point"], flows["work_point"])]

    flows.drop(columns=["home_coords", "home_point", "work_coords", "work_point"], inplace=True)

    flows = flows.replace({np.nan: None})

    flows["gender"] = flows["gender"].replace({"1": "m", "2": "f"})
    flows["typmr"] = flows["typmr"].replace({
        "11": "1",
        "12": "1",
        "31": "2",
        "32": "2",
        "42": "3",
        "43": "3",
        "41": "4",
        "ZZ": "5",
        "20": "5",
        "44": "5",
    })

    flows["mesh"] = "epci"
    flows_epci = flows

    print((flows_com["distance"] * flows_com["flow"]).sum() / flows_com["flow"].sum())
    print((flows_epci["distance"] * flows_epci["flow"]).sum() / flows_epci["flow"].sum())

    flows = pd.concat([flows_com, flows_epci])
    print(flows)

    flows_com = flows_com.groupby(["home_geo_code", "home_lat", "home_lon",
                                   "work_geo_code", "work_lat", "work_lon"], as_index=False).agg(**{
        "distance": pd.NamedAgg(column="distance", aggfunc="first"),
        "flow": pd.NamedAgg(column="flow", aggfunc="sum"),
    })
    print(flows_com)

    def osrm_dist(row):
        f_lon, f_lat, t_lon, t_lat = row["home_lon"], row["home_lat"], row["work_lon"], row["work_lat"]
        resp = requests.get(
            f"http://router.project-osrm.org/route/v1/driving/{f_lon},{f_lat};{t_lon},{t_lat}?overview=false")
        print(resp)
        return round(resp.json()["routes"][0]["distance"] / 1000, 1)

    flows_com["distance2"] = flows_com.apply(osrm_dist, axis=1, result_type="reduce")
    print(flows_com)
    print(flows_com.head(50))
    print((flows_com["distance"] * flows_com["flow"]).sum() / flows_com["flow"].sum())
    print((flows_com["distance2"] * flows_com["flow"]).sum() / flows_com["flow"].sum())

    mask_distance_null = flows_com["distance"] < 0.1

    flows_com2 = flows_com.loc[~mask_distance_null]
    print(flows_com2)
    print(flows_com2.head(50))
    print((flows_com2["distance"] * flows_com2["flow"]).sum() / flows_com2["flow"].sum())
    print((flows_com2["distance2"] * flows_com2["flow"]).sum() / flows_com2["flow"].sum())

    return {
        "work_flows": flows.to_dict(orient="list")
    }


class WorkFlows(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("work flows", geo_codes)
        return get_work_flows(geo_codes)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)

    cc_haut_lignon = ["43069", "43244", "43129", "43199", "43130", "43051"]
    cc_chamonix_mt = ["74290", "74056", "74143", "74266"]
    cc_rives_haut_allier = ["43006", "43009", "43011", "43015", "43027", "43031", "43044", "43054", "43056", "43060",
                            "43063", "43065", "43067", "43068", "43070", "43075", "43079", "43082", "43083", "43085",
                            "43086", "43090", "43094", "43104", "43106", "43107", "43029", "43072", "43112", "43118",
                            "43131", "43132", "43133", "43139", "43148", "43149", "43151", "43155", "43232", "43234",
                            "43239", "43167", "43169", "43171", "43175", "43178", "43188", "43202", "43214", "43219",
                            "43222", "43183", "43208", "43242", "43245", "43250", "43252", "43256", "43264", "43013"]
    flows = get_work_flows(cc_rives_haut_allier)
