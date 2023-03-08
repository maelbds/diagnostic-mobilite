import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.ign.commune_outline import get_commune_outline


"""
Functions to get public transport info from database.

Process is the following :
1. Get all stops into a rectangle area with get_stops_in_area
(2. Filter and keep stops which are really into the desired communes) -> not inside this file
3. From stops ids, get the associated routes_id | get_routes_from_stop()
4. Get all routes of the area | get_all_routes_from_stops()
5. From routes_id, get all associated trips_id | get_trips_from_route()
6. From trips_id, get the path with ordered stops and their coordinates | get_stops_from_trips()
7. -> 5-6 used here to get all trips and associated stops | get_complete_trips_from_routes()

JOIN SQL requests are too slow, that is why simple requests are used and join operations are done with Pandas DataFrame
"""


def get_stops_in_area(pool, min_lat, max_lat, min_lon, max_lon):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT datagouv_id, 
                          stop_id, 
                          stop_name, 
                          stop_lat, 
                          stop_lon 
                FROM datagouv_pt_stops 
                WHERE (?<stop_lat AND stop_lat<? AND ?<stop_lon AND stop_lon<?) 
                """, [min_lat, max_lat, min_lon, max_lon])
    result = list(cur)
    stops = pd.DataFrame(result, columns=["datagouv_id", "stop_id", "stop_name", "stop_lat", "stop_lon"])
    conn.close()
    return stops


def get_trips_from_stops(pool, stops):
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    def request(dg_id, stop_id):
        cur.execute("""SELECT datagouv_id, trip_id 
                FROM datagouv_pt_stop_times 
                WHERE datagouv_id=? AND stop_id=? 
                """, [dg_id, stop_id])
        result = list(cur)
        r_trips = pd.DataFrame(result, columns=["datagouv_id", "trip_id"])
        return r_trips

    new_trips = [request(dg_id, stop_id) for dg_id, stop_id in zip(stops["datagouv_id"], stops["stop_id"])]
    print("new trips")
    if len(new_trips) > 0:
        trips = pd.concat(new_trips)

        trips = trips.drop_duplicates()
        conn.close()
        return trips
    else:
        return pd.DataFrame(columns=["datagouv_id", "trip_id"])


def get_routes_id_from_trips(pool, trips):
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    def request(dg_id, trip_id):
        cur.execute("""SELECT datagouv_id, 
                              route_id,
                              trip_id  
                    FROM datagouv_pt_trips
                    WHERE datagouv_id=? AND trip_id=? 
                    """, [dg_id, trip_id])
        result = list(cur)
        r_routes_id = pd.DataFrame(result, columns=["datagouv_id", "route_id", "trip_id"])
        return r_routes_id

    new_routes_id = [request(dg_id, trip_id) for dg_id, trip_id in zip(trips["datagouv_id"], trips["trip_id"])]
    if len(new_routes_id) > 0:
        routes_id = pd.concat(new_routes_id)
        routes_id = routes_id.drop_duplicates()
        conn.close()
        return routes_id
    else:
        return pd.DataFrame(columns=["datagouv_id", "route_id", "trip_id"])


def get_routes_from_routes_id(pool, routes_id):
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    def request(dg_id, route_id):
        cur.execute("""SELECT datagouv_id, 
                              route_id, 
                              route_short_name, 
                              route_long_name, 
                              route_type 
                    FROM datagouv_pt_routes  
                    WHERE datagouv_id=? AND route_id=? 
                    """, [dg_id, route_id])
        result = list(cur)
        r_routes = pd.DataFrame(result, columns=["datagouv_id", "route_id", "route_short_name", "route_long_name",
                                                 "route_type"])
        return r_routes

    new_routes = [request(dg_id, route_id) for dg_id, route_id in zip(routes_id["datagouv_id"], routes_id["route_id"])]
    if len(new_routes) > 0:
        routes = pd.concat(new_routes)
        routes = routes.drop_duplicates()
        conn.close()
        return routes
    else:
        return pd.DataFrame(columns=["datagouv_id", "route_id", "route_short_name", "route_long_name",
                                     "route_type"])


def get_stops_sequence_from_trips(pool, trips):
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    def request(dg_id, trip_id):
        cur.execute("""SELECT datagouv_id, trip_id, stop_id, stop_sequence     
                    FROM datagouv_pt_stop_times  
                    WHERE datagouv_id=? AND trip_id=? 
                    """, [dg_id, trip_id])
        result = list(cur)
        r_stops_sequence = pd.DataFrame(result, columns=["datagouv_id", "trip_id", "stop_id", "stop_sequence"])
        return r_stops_sequence

    new_stops_sequence = [request(dg_id, trip_id) for dg_id, trip_id in zip(trips["datagouv_id"], trips["trip_id"])]
    if len(new_stops_sequence) > 0:
        stops_sequence = pd.concat(new_stops_sequence)
        stops_sequence = stops_sequence.drop_duplicates()
        conn.close()
        return stops_sequence
    else:
        return pd.DataFrame(columns=["datagouv_id", "trip_id", "stop_id", "stop_sequence"])


def get_stops_from_stops_sequence(pool, stops_sequence):
    stops_sequence = stops_sequence.drop(columns=["trip_id", "stop_sequence"])
    stops_sequence = stops_sequence.drop_duplicates()
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    def request(dg_id, stop_id):
        cur.execute("""SELECT datagouv_id, 
                          stop_id, 
                          stop_name, 
                          stop_lat, 
                          stop_lon 
                    FROM datagouv_pt_stops  
                    WHERE datagouv_id=? AND stop_id=? 
                    """, [dg_id, stop_id])
        result = list(cur)
        r_stops = pd.DataFrame(result, columns=["datagouv_id", "stop_id", "stop_name", "stop_lat", "stop_lon"])
        return r_stops

    new_stops = [request(dg_id, stop_id) for dg_id, stop_id in zip(stops_sequence["datagouv_id"],
                                                                   stops_sequence["stop_id"])]
    if len(new_stops) > 0:
        stops = pd.concat(new_stops)
        stops = stops.drop_duplicates()
        conn.close()
        return stops
    else:
        return pd.DataFrame(columns=["datagouv_id", "stop_id", "stop_name", "stop_lat", "stop_lon"])


""" Functions to group previous basic functions """


def get_detailed_trips_from_stops(pool, stops):
    trips = get_trips_from_stops(pool, stops)
    print("trips")

    routes_id = get_routes_id_from_trips(pool, trips)
    print("routes id")
    routes = get_routes_from_routes_id(pool, routes_id)
    print("route")

    stops_sequence = get_stops_sequence_from_trips(pool, trips)
    print("stops sequence")
    all_stops = get_stops_from_stops_sequence(pool, stops_sequence)

    detailed_trips = pd.merge(stops_sequence, all_stops, how="inner", left_on=["datagouv_id", "stop_id"],
                              right_on=["datagouv_id", "stop_id"])
    detailed_trips = pd.merge(detailed_trips, routes_id, how="inner", left_on=["datagouv_id", "trip_id"],
                              right_on=["datagouv_id", "trip_id"])
    detailed_trips = pd.merge(detailed_trips, routes, how="inner", left_on=["datagouv_id", "route_id"],
                              right_on=["datagouv_id", "route_id"])
    return detailed_trips


def get_public_transport_from_detailed_trips(detailed_trips):
    public_transport = []

    routes = detailed_trips[["datagouv_id", "route_id", "route_short_name", "route_long_name", "route_type"]]
    routes = routes.drop_duplicates()

    for dg_id, route_id, route_short_name, route_long_name, route_type in zip(
            routes["datagouv_id"], routes["route_id"], routes["route_short_name"],
            routes["route_long_name"], routes["route_type"]):

        detailed_trips_grouped_by_trip = detailed_trips[
            (detailed_trips["route_id"] == route_id) & (detailed_trips["datagouv_id"] == dg_id)
            ].groupby(["trip_id"]).agg(["count"])
        main_trip_id = detailed_trips_grouped_by_trip.idxmax()["datagouv_id"]["count"]

        main_trip = detailed_trips[
            (detailed_trips["datagouv_id"] == dg_id) & (detailed_trips["trip_id"] == main_trip_id)]
        main_trip = main_trip.sort_values(by=["stop_sequence"])

        public_transport.append(
            {"route_id": route_id,
             "route_short_name": route_short_name,
             "route_long_name": route_long_name,
             "route_type": route_type,
             "stop_name": main_trip["stop_name"],
             "stop_lat": main_trip["stop_lat"],
             "stop_lon": main_trip["stop_lon"]}
        )

        if __name__ == '__main__':
            from matplotlib import pyplot as plt
            plt.plot(main_trip["stop_lon"], main_trip["stop_lat"])
            plt.title(route_short_name + " - " + route_long_name)
            plt.axis('equal')
            plt.show()

    return public_transport


def get_public_transport(pool, geo_codes):
    outlines = [sum(get_commune_outline(pool, geo_code), []) for geo_code in geo_codes]

    min_lat = min([min(np.array(outline)[:, 0]) for outline in outlines])
    max_lat = max([max(np.array(outline)[:, 0]) for outline in outlines])
    min_lon = min([min(np.array(outline)[:, 1]) for outline in outlines])
    max_lon = max([max(np.array(outline)[:, 1]) for outline in outlines])

    def stop_is_in_territory(stop):
        stop_lat = stop["stop_lat"]
        stop_lon = stop["stop_lon"]
        return any([Point(stop_lat, stop_lon).within(Polygon(outline)) for outline in outlines])

    stops_in_area = get_stops_in_area(pool, min_lat, max_lat, min_lon, max_lon)
    print(stops_in_area)
    print(stops_in_area["datagouv_id"].drop_duplicates())
    stops_in_territory = stops_in_area[stops_in_area.apply(stop_is_in_territory, axis=1)]
    print("stops in territory done")

    detailed_trips = get_detailed_trips_from_stops(pool, stops_in_territory)
    print(detailed_trips)
    print("detailed trips done")
    public_transport = get_public_transport_from_detailed_trips(detailed_trips)
    print("get public transport done")
    return public_transport


""" TO COMPLETE : Functions to get unique segments of route network from all trips."""


def merge_routes(route1, route2):
    segments1notin2 = [sgmt for sgmt in route1 if set(route1) not in [set(sgmnt2) for sgmnt2 in route2]]
    segments2notin1 = [sgmt for sgmt in route2 if set(route2) not in [set(sgmnt1) for sgmnt1 in route1]]

    merged_route = [sgmt for sgmt in route1 if set(route1) in [set(sgmnt2) for sgmnt2 in route2]]
    """
    Identifier les segments qui ne sont pas en commun.
    Pour chacun d'entre eux : est-ce qu'il y a des segements communs avant et après : 
        - si oui : on garde le plus long chemin
        - si non : on les ajoute 
    """
    return merged_route


def get_main_trips_from_geo_codes(pool, geo_codes):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT g.datagouv_id, 
                          g.route_id,
                          r.route_short_name, r.route_long_name, r.route_type,
                          t.trip_id,
                          st.stop_id, st.stop_sequence,
                          s.stop_name, s.stop_lat, s.stop_lon
                FROM datagouv_pt_geocodes AS g
                JOIN datagouv_pt_routes AS r ON g.datagouv_id = r.datagouv_id AND g.route_id = r.route_id
                JOIN datagouv_pt_trips AS t ON g.datagouv_id = t.datagouv_id AND g.main_trip_id = t.trip_id
                JOIN datagouv_pt_stop_times AS st ON g.datagouv_id = st.datagouv_id AND t.trip_id = st.trip_id
                JOIN datagouv_pt_stops AS s ON g.datagouv_id = s.datagouv_id AND st.stop_id = s.stop_id
                WHERE g.geo_code IN (""" + ",".join(["?" for g in geo_codes]) + ")", geo_codes)
    result = list(cur)
    conn.close()
    main_trips = pd.DataFrame(result, columns=["datagouv_id",
                                                   "route_id",
                                                   "route_short_name", "route_long_name", "route_type",
                                                   "trip_id",
                                                   "stop_id", "stop_sequence",
                                                   "stop_name", "stop_lat", "stop_lon"])
    return main_trips


def get_public_transport2(pool, geo_codes):  # WORK IN PROGRESS
    public_transport = []
    main_trips = get_main_trips_from_geo_codes(pool, geo_codes)
    main_trips = main_trips.sort_values(by=["route_id", "trip_id", "stop_sequence"])

    main_trips.groupby(by="trip_id").apply(lambda df: public_transport.append(
        {"route_id": df["route_id"].iloc[0],
         "route_short_name": df["route_short_name"].iloc[0],
         "route_long_name": df["route_long_name"].iloc[0],
         "route_type": df["route_type"].iloc[0],
         "stop_name": df["stop_name"],
         "stop_lat": df["stop_lat"],
         "stop_lon": df["stop_lon"]}
    ))

    if __name__ == '__main__' and False:
        for pt in public_transport:
            print(pt.to_dict())
            pt.plot_route()

    return public_transport


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)
    """
    route_id_test = "DSE:Line:1001009"
    datagouv_id_test = "73b1b1ee-2b81-445f-8930-b95a2b28a81b"
    trip_id_test = "DSE:VehicleJourney:1006457-1006633"
    stop_id_test = "NAQ:Quay:19400"
    """
    get_public_transport2(None, ["69123"])
    public_transport_test = get_public_transport(None, ["79048"])
    for p in public_transport_test:
        p.presentation()

    """
    trip1 = ["a", "b", "c", "d", "e"]
    trip2 = ["f", "b", "c", "g", "h", "d", "e"]

    route1 = route_from_stops_list(trip1)
    route2 = route_from_stops_list(trip2)

    merged_route = merge_routes(route1, route2)
    """
