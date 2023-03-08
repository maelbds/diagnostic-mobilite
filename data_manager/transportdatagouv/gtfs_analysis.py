import pandas as pd
from shapely.geometry import Point


def gtfs_to_geo_codes(datagouv_id, routes_df, trips_df, stops_df, stop_times_df, communes_outline):
    def lat_lon_to_point(row):
        lat = row["stop_lat"]
        lon = row["stop_lon"]
        return Point(lon, lat)

    stops_df = stops_df.astype({"stop_lat": "float64", "stop_lon": "float64"})
    stops_df["shp_point"] = stops_df.apply(lambda row: lat_lon_to_point(row), axis=1)

    def find_geocode(row):
        point = row["shp_point"]
        mask_commune = communes_outline["outline"].apply(lambda outline: point.within(outline))
        if len(communes_outline[mask_commune]["geo_code"]) > 1:
            print(communes_outline[mask_commune]["geo_code"])
            print("---")
        return communes_outline.loc[mask_commune]["geo_code"].iloc[0]
    stops_df["geo_code"] = stops_df.apply(lambda row: find_geocode(row), axis=1)

    stop_times_stop = pd.merge(stop_times_df, stops_df, on="stop_id")
    trips_stop_times = pd.merge(stop_times_stop, trips_df, on="trip_id")
    routes_trips = pd.merge(trips_stop_times, routes_df, on="route_id")

    routes_main_trip = routes_trips.groupby(by="route_id").apply(lambda df: df.groupby("trip_id").count().idxmax()["route_id"])
    routes_main_trip = routes_main_trip.rename("main_trip_id")

    routes_geo_codes = routes_trips[["route_id", "geo_code"]].drop_duplicates()

    routes_trips_geo_codes = pd.merge(routes_geo_codes, routes_main_trip, left_on="route_id", right_index=True)

    return routes_trips_geo_codes


