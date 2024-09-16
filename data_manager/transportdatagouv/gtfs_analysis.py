import pandas as pd
import numpy as np
from shapely.geometry import Point


def gtfs_to_geo_codes(datagouv_id, routes_df, trips_df, stops_df, stop_times_df, communes_outline):

    stops_df = stops_df.astype({"stop_lat": "float64", "stop_lon": "float64"})
    stops_df["shp_point"] = [Point(lon, lat) for lat, lon in zip(stops_df["stop_lat"], stops_df["stop_lon"])]

    def find_geocode(point):
        x = point.x
        y = point.y

        mask_communes_not_to_check = (communes_outline["miny"] > y) | \
                                     (communes_outline["maxy"] < y) | \
                                     (communes_outline["minx"] > x) | \
                                     (communes_outline["maxx"] < x)

        communes_to_check = communes_outline[~mask_communes_not_to_check]
        mask_commune = communes_to_check["outline"].apply(lambda outline: point.within(outline))
        if len(communes_to_check[mask_commune]) > 1:
            print(communes_to_check[mask_commune]["geo_code"])
            print("---")
            return communes_to_check.loc[mask_commune]["geo_code"].iloc[0]
        elif len(communes_to_check[mask_commune]) == 1:
            return communes_to_check.loc[mask_commune]["geo_code"].iloc[0]
        else:
            return None

    stops_df["geo_code"] = [find_geocode(point) for point in stops_df["shp_point"]]
    stops_df = stops_df.dropna(subset=["geo_code"])

    print("found stops geo_code")

    stop_times_stop = pd.merge(stop_times_df[["stop_id", "trip_id"]], stops_df[["stop_id", "geo_code"]], on="stop_id")
    trips_stop_times = pd.merge(stop_times_stop[["trip_id", "geo_code"]], trips_df[["trip_id", "route_id"]], on="trip_id")
    routes_trips = pd.merge(trips_stop_times[["route_id", "trip_id", "geo_code"]], routes_df[["route_id"]], on="route_id")

    routes_main_trip = routes_trips.groupby(by="route_id").apply(
        lambda df: df.groupby("trip_id").count().idxmax()["route_id"])
    routes_main_trip = routes_main_trip.rename("main_trip_id")

    routes_geo_codes = routes_trips[["route_id", "geo_code"]].drop_duplicates()
    routes_trips_geo_codes = pd.merge(routes_geo_codes, routes_main_trip, left_on="route_id", right_index=True)

    return routes_trips_geo_codes
