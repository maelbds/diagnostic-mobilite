import pprint
import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError
from data_manager.ign.commune_center import get_coords
from data_manager.insee_general.districts import get_districts
from data_manager.osm.functions_geography import distance_pt_pt

from data_manager.insee_mobpro.source import SOURCE_MOBPRO


WORK_FLOWS_THRESHOLD = 10


def get_flows_home_work_bdd(pool, geo_code, source):
    """
    Get the work destination and flow of employed people living in given geo_code commune
    :param geo_code: geo_code of the concerned commune
    :param source: source to use
    :return: List of tuples with destination communes and associated geo_code, name, lat, lon, flow
    """
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT geo_code_work, name, lat, lon, SUM(flow) 
                FROM insee_flows_home_work 
                INNER JOIN insee_communes
                ON geo_code_work = geo_code
                WHERE geo_code_home = ? AND source = ?
                GROUP BY geo_code_work
                """, [geo_code, source])
    flows = list(cur)
    conn.close()
    return flows


def get_flows_home_work_trans(pool, geo_code, source=SOURCE_MOBPRO):
    """
    Get the work destination and flow of employed people living in given geo_code commune
    :param geo_code: geo_code of the concerned commune
    :param source: source to use
    :return: List of tuples with destination communes and associated geo_code, name, lat, lon, flow
    """
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT insee_flows_home_work.geo_code_work, insee_arrondissements.geo_code_city, lat, lon, TRANS, flow 
                FROM insee_flows_home_work 
                LEFT JOIN insee_arrondissements ON insee_flows_home_work.geo_code_work = insee_arrondissements.geo_code_district
                INNER JOIN insee_communes ON geo_code_work = geo_code
                WHERE geo_code_home = ? AND source = ?""", [geo_code, source])
    result = list(cur)

    # districts management
    flows = pd.DataFrame(result, columns=["geo_code_work_district", "geo_code_work_city", "lat", "lon", "work_transport", "flow"])

    mask_no_city = flows["geo_code_work_city"].isna()
    flows.loc[mask_no_city, "geo_code_work_city"] = flows.loc[mask_no_city, "geo_code_work_district"]
    flows["geo_code_work"] = flows["geo_code_work_city"]
    flows.drop(columns=["geo_code_work_city", "geo_code_work_district"], inplace=True)

    #  80km, low distance mobility
    coords_home = get_coords(pool, geo_code)
    flows["distance"] = flows.apply(lambda row: distance_pt_pt(coords_home, [row["lat"], row["lon"]]), axis=1)
    flows = flows[flows["distance"] < 80*1000]
    flows.drop(columns=["distance", "lat", "lon"], inplace=True)

    total_flows_by_dest = flows[["geo_code_work", "flow"]].groupby(by="geo_code_work").sum().reset_index().rename(columns={"flow": "total_flow"})
    flows = pd.merge(flows, total_flows_by_dest, on="geo_code_work")
    flows = flows[flows["total_flow"].round() >= WORK_FLOWS_THRESHOLD]
    flows.drop(columns=["total_flow"])

    #
    flows_geo_code = flows[["geo_code_work", "flow"]].groupby(by="geo_code_work").sum()
    flows_geo_code = flows_geo_code/flows_geo_code.sum()

    flows_mode = flows[["work_transport", "flow"]].groupby(by="work_transport").sum()
    flows_mode = flows_mode/flows_mode.sum()

    flows_transport_mode_geo_code = flows.groupby(by=["work_transport"]).apply(lambda df: df[["geo_code_work", "flow"]].groupby(by="geo_code_work").sum()/df["flow"].sum())
    flows_transport_geo_code_mode = flows.groupby(by=["geo_code_work"]).apply(lambda df: df[["work_transport", "flow"]].groupby(by="work_transport").sum()/df["flow"].sum())

    conn.close()
    return flows_geo_code, flows_transport_mode_geo_code, flows_mode, flows_transport_geo_code_mode


def get_flows_home_work_workers_bdd(pool, geo_code, source):
    """
    Get the work destination and flow of employed people living in given geo_code commune
    :param geo_code: geo_code of the concerned commune
    :param source: source to use
    :return: List of tuples with destination communes and associated geo_code, name, lat, lon, flow
    """
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT geo_code_home, name, lat, lon, SUM(flow) 
                FROM insee_flows_home_work 
                INNER JOIN insee_communes
                ON geo_code_home = geo_code
                WHERE geo_code_work = ? AND source = ?
                GROUP BY geo_code_home""", [geo_code, source])
    flows = list(cur)
    conn.close()
    return flows


def group_districts_into_city(pool, flows):
    district_df = get_districts(pool)
    flows_df = pd.DataFrame(flows, columns=["code_district", "name", "lat", "lon", "flow"])
    flows_df = pd.merge(flows_df, district_df, left_on="code_district", right_on="district", how="left")
    flows_df.loc[flows_df["city"].isna(), "city"] = flows_df.loc[flows_df["city"].isna(), "code_district"]
    flows_df["code_district"] = flows_df["city"]
    flows_df = flows_df.drop(columns=["district", "city"])
    flows_df_grouped = flows_df[["code_district", "flow"]].groupby("code_district").sum()
    flows_df = flows_df.drop_duplicates(subset="code_district").drop(columns=["flow"])
    flows_df = flows_df.merge(flows_df_grouped, on="code_district")
    return flows_df.to_dict(orient="split")["data"]


def get_flows_home_work(pool, geo_code, source=SOURCE_MOBPRO):
    flows_bdd = get_flows_home_work_bdd(pool, geo_code, source)
    coords_home = get_coords(pool, geo_code)
    flows = group_districts_into_city(pool, flows_bdd)
    flows = [[geo_code_d, name, lat, lon, round(flow)] for geo_code_d, name, lat, lon, flow in flows
             if lat is not None and distance_pt_pt(coords_home, [lat, lon]) < 80 * 1000 and geo_code_d != geo_code]
             #  80km, low distance mobility
    return flows


def get_flows_home_work_workers(pool, geo_codes, source=SOURCE_MOBPRO):
    all_flows = []
    for geo_code in geo_codes:
        flows_bdd = get_flows_home_work_workers_bdd(pool, geo_code, source)
        coords_home = get_coords(pool, geo_code)
        flows = group_districts_into_city(pool, flows_bdd)
        flows = [[geo_code_d, name, lat, lon, flow] for geo_code_d, name, lat, lon, flow in flows
                 if lat is not None and distance_pt_pt(coords_home, [lat, lon]) < 80 * 1000 and geo_code_d != geo_code]
                 #  80km, low distance mobility
        all_flows += flows

    all_flows_df = pd.DataFrame(all_flows, columns=["geo_code", "name", "lat", "lon", "flow"])
    all_flows_df = all_flows_df.groupby("geo_code", as_index=False).agg({
            "name": lambda col: col.iloc[0],
            "lat": lambda col: col.iloc[0],
            "lon": lambda col: col.iloc[0],
            "flow": lambda col: col.sum().round(),
        })
    all_flows = all_flows_df.to_dict(orient="split")["data"]
    return all_flows


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pd.set_option('display.max_columns', 50)
        pd.set_option('display.max_rows', 50)
        pd.set_option('display.width', 2000)
        geo_codes =[] # ['84147', '84133', '84113', '84084', '84076', '84026', '84024', '84014', '84010', '84002', '84151', '84121', '84090', '84052', '84042', '84009']
        for g in geo_codes:
            print(g)
            flows_by_geo_code, flows_by_mode_and_geocode, flows_by_mode, flows_transport_geo_code_mode = get_flows_home_work_trans(None, g, "MOBPRO_2018")
            #print(flows_by_transport_mode.loc[5])
            print(flows_by_mode_and_geocode)
            print(flows_by_geo_code)
            print(flows_by_mode)
            print(flows_transport_geo_code_mode)


        """
        cachan_flows_geo_code, cachan_flows_transport_mode_geo_code, cachan_flows_mode, cachan_flows_transport_geo_code_mode  = get_flows_home_work_trans(None, "94016", "MOBPRO_2018")

        print(cachan_flows_mode)
        print(cachan_flows_geo_code)
        main_geocodes = cachan_flows_geo_code.sort_values(by="flow", ascending=False).head(25).index.to_list()
        print(main_geocodes)

        from model.functions.osrm import itinerary_osrm

        def calc_osrm_dist(coord1, coord2):
            return itinerary_osrm(coord1, coord2)["distance"]

        main_distances = [round(calc_osrm_dist(get_coords(None, "94016"), get_coords(None, g))/1000, 1) for g in main_geocodes]

        print(main_distances)
        print(pd.DataFrame(index=main_geocodes, data={"distance": main_distances}))

        print(cachan_flows_transport_geo_code_mode.loc[main_geocodes].xs(6, level=1))
        print(cachan_flows_transport_geo_code_mode.loc["94003"])
        print(cachan_flows_transport_geo_code_mode.xs("94016", level=0))"""

        print(get_flows_home_work(None, "69050", "MOBPRO_2018"))
        print(sum([f[4] for f in get_flows_home_work(None, "69009", "MOBPRO_2018") if f[4] < 10]))

        print(get_flows_home_work_workers(None, ["34172"]))

        """
        print(flows[flows["name"]=="LA CRECHE"])
        flows = get_flows_home_work(None, "79048", "MOBPRO_2018")
        print(flows)
        flows20 = [ f for f in flows if f[4]>20]
        print(flows20)
        pprint.pprint(len(flows20))
        print(f"Total flux {sum([f[4] for f in flows])}")
        flows_workers = get_flows_home_work_workers(None, ["79048"], "MOBPRO_2018")
        pprint.pprint(flows_workers)"""
    except UnknownGeocodeError as e:
        print(e.message)
