import pandas as pd
import numpy as np
from pyproj import Transformer
from shapely import Point, distance

from compute_model.v_database_connection.db_request import db_request
from compute_model.sources import sources

WORK_FLOWS_THRESHOLD_FLOW = 10
WORK_FLOWS_THRESHOLD_DISTANCE = 80 # km


def get_flows_home_work(geo_codes):
    result = db_request(
        """ SELECT  f.CODGEO_home, c1.chflieu_lat, c1.chflieu_lon, c1.centroid_lat, c1.centroid_lon, 
                    f.CODGEO_work, c2.chflieu_lat, c2.chflieu_lon, c2.centroid_lat, c2.centroid_lon, 
                    f.TRANS, f.SEXE, f.CS1, f.TYPMR, f.flow
            FROM insee_flows_mobpro AS f
            LEFT JOIN ign_commune_center AS c1 ON f.CODGEO_home = c1.geo_code
            LEFT JOIN ign_commune_center AS c2 ON f.CODGEO_work = c2.geo_code
            WHERE f.CODGEO_home IN :geo_codes
            AND f.year_data = :year_mobpro
        """,
        {
            "geo_codes": geo_codes,
            "year_mobpro": sources["mobpro"]["year"],
        }
    )

    flows = pd.DataFrame(result, columns=["home_geo_code", "home_chflieu_lat", "home_chflieu_lon", "home_lat", "home_lon",
                                          "work_geo_code", "work_chflieu_lat", "work_chflieu_lon", "work_lat", "work_lon",
                                          "mode", "gender", "csp", "typmr", "flow"])

    mask_no_chflieu_home = flows["home_chflieu_lat"].isna() | flows["home_chflieu_lon"].isna()
    mask_no_chflieu_work = flows["work_chflieu_lat"].isna() | flows["work_chflieu_lon"].isna()

    flows.loc[~mask_no_chflieu_home, "home_lat"] = flows["home_chflieu_lat"]
    flows.loc[~mask_no_chflieu_home, "home_lon"] = flows["home_chflieu_lon"]
    flows.loc[~mask_no_chflieu_work, "work_lat"] = flows["work_chflieu_lat"]
    flows.loc[~mask_no_chflieu_work, "work_lon"] = flows["work_chflieu_lon"]
    flows.drop(columns=["home_chflieu_lat", "home_chflieu_lon", "work_chflieu_lat", "work_chflieu_lon"], inplace=True)

    # set same work commune as home when mode = no travel
    mask_mode_1 = flows["mode"] == "1"
    flows.loc[mask_mode_1, "work_geo_code"] = flows.loc[mask_mode_1, "home_geo_code"]
    flows.loc[mask_mode_1, "work_lat"] = flows.loc[mask_mode_1, "home_lat"]
    flows.loc[mask_mode_1, "work_lon"] = flows.loc[mask_mode_1, "home_lon"]

    # only keep mode as attribute
    flows = flows.groupby(by=["home_geo_code", "work_geo_code", "mode"], as_index=False).agg(**{
        "home_lat": pd.NamedAgg(column="home_lat", aggfunc="first"),
        "home_lon": pd.NamedAgg(column="home_lon", aggfunc="first"),
        "work_lat": pd.NamedAgg(column="work_lat", aggfunc="first"),
        "work_lon": pd.NamedAgg(column="work_lon", aggfunc="first"),
        "flow": pd.NamedAgg(column="flow", aggfunc=lambda x: x.sum().round())
    })

    # remove flows out of France (with no coords)
    flows.dropna(subset=["work_lat", "work_lon"], inplace=True)

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

    flows.drop(columns=["home_coords", "home_point", "work_coords", "work_point",
                        "home_lat", "home_lon", "work_lat", "work_lon"], inplace=True)

    # keep only significant flows
    # mask_significant_flows = flows["flow"] > WORK_FLOWS_THRESHOLD_FLOW
    # keep only flows within low distance mobility
    mask_inside_perimeter_flows = flows["distance"] < WORK_FLOWS_THRESHOLD_DISTANCE

    flows = flows.loc[mask_inside_perimeter_flows]
    return flows


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    result = db_request(
        """ SELECT CODGEO
            FROM insee_epci_communes
            WHERE EPCI = '200040491'
        """,
        {}
    )
    geocodes = pd.DataFrame(result, columns=["geo_code"])["geo_code"].to_list()
    print(geocodes)

    print(get_flows_home_work(geocodes))

