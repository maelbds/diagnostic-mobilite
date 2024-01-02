import pandas as pd
from pyproj import Transformer

from compute_model.v_database_connection.db_request import db_request
from compute_model.sources import sources


def get_all_pt(geo_codes):
    result = db_request(
        """
        SELECT g.datagouv_id,  g.route_id,
               r.route_short_name, r.route_long_name, r.route_type,
               t.trip_id,
               st.stop_id, st.stop_sequence,
               s.stop_name, s.stop_lat, s.stop_lon
        FROM datagouv_pt_geocodes AS g
        LEFT JOIN datagouv_pt_routes AS r ON g.datagouv_id = r.datagouv_id AND g.route_id = r.route_id
        LEFT JOIN datagouv_pt_trips AS t ON g.datagouv_id = t.datagouv_id AND g.main_trip_id = t.trip_id
        LEFT JOIN datagouv_pt_stop_times AS st ON g.datagouv_id = st.datagouv_id AND t.trip_id = st.trip_id
        LEFT JOIN datagouv_pt_stops AS s ON g.datagouv_id = s.datagouv_id AND st.stop_id = s.stop_id
        WHERE g.geo_code IN :geo_codes
        """,
        {
            "geo_codes": geo_codes
        }
    )

    all_pt = pd.DataFrame(result, columns=["datagouv_id", "route_id",
                                           "route_short_name", "route_long_name", "route_type",
                                           "trip_id",
                                           "stop_id", "stop_sequence",
                                           "stop_name", "stop_lat", "stop_lon"])
    return all_pt


def get_public_transport(geo_codes):
    all_pt = get_all_pt(geo_codes)
    all_pt = all_pt.sort_values(by=["route_id", "trip_id", "stop_sequence"])

    pt_stops = all_pt[["stop_id", "stop_name", "stop_lat", "stop_lon"]].drop_duplicates()

    pt_routes = all_pt.groupby(by="trip_id").agg(**{
        "id": pd.NamedAgg(column="route_id", aggfunc="first"),
        "short_name": pd.NamedAgg(column="route_short_name", aggfunc="first"),
        "long_name": pd.NamedAgg(column="route_long_name", aggfunc="first"),
        "type": pd.NamedAgg(column="route_type", aggfunc="first"),
        "stops_name": pd.NamedAgg(column="stop_name", aggfunc=list),
        "stops_lat": pd.NamedAgg(column="stop_lat", aggfunc=list),
        "stops_lon": pd.NamedAgg(column="stop_lon", aggfunc=list),
    })
    return pt_routes, pt_stops


def get_train_stations(geo_codes):
    result = db_request(
        """ SELECT insee_bpe.id, types.name, insee_bpe.lat, insee_bpe.lon
            FROM insee_bpe 
            JOIN insee_bpe_types 
            ON insee_bpe.id_type = insee_bpe_types.id
            JOIN types 
            ON insee_bpe_types.id_type = types.id
            WHERE insee_bpe.geo_code IN :geo_codes 
            AND year_data = :year_data
            AND insee_bpe_types.id_type = 32
            """,
            {
                "geo_codes": geo_codes,
                "year_data": sources["bpe"]["year"]
            }
    )
    train_stations = pd.DataFrame(result, columns=["id", "name", "lat", "lon"])
    return train_stations


def get_pt_stops(geo_codes):
    pt_routes, pt_stops = get_public_transport(geo_codes)
    train_stations = get_train_stations(geo_codes)

    pt_stops = pt_stops.rename(columns=lambda x: x.replace("stop_", ""))

    all_pt_stops = pd.concat([pt_stops, train_stations])
    all_pt_stops["coords_geo"] = [[lat, lon] for lat, lon in zip(all_pt_stops["lat"], all_pt_stops["lon"])]

    # Geo to Lambert93 coordinates system :
    transformer2154 = Transformer.from_crs("epsg:4326",  # World Geodetic System (lat/lon)
                                           "epsg:2154")  # Lambert 93 (x, y)

    def geo_to_lambert(lat, lon):
        x, y = transformer2154.transform(lat, lon)
        return [round(x), round(y)]

    all_pt_stops["coords_lamb"] = [geo_to_lambert(lat, lon) for lat, lon
                                   in zip(all_pt_stops["lat"], all_pt_stops["lon"])]

    return all_pt_stops


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)
    get_public_transport(["79048"])
    print(get_train_stations(["79048"]))
    print(get_pt_stops(["01004", "01002"]))

