import pandas as pd

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_public_transport(geo_codes):
    result = db_request(
        """ SELECT g.datagouv_id, 
                  g.route_id,
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

    main_trips = pd.DataFrame(result, columns=["datagouv_id",
                                               "route_id",
                                               "route_short_name", "route_long_name", "route_type",
                                               "trip_id",
                                               "stop_id", "stop_sequence",
                                               "stop_name", "stop_lat", "stop_lon"])

    main_trips = main_trips.sort_values(by=["route_id", "trip_id", "stop_sequence"])
    main_trips = main_trips.groupby(by="trip_id").agg(**{
        "route_id": pd.NamedAgg(column="route_id", aggfunc="first"),
        "route_short_name": pd.NamedAgg(column="route_short_name", aggfunc="first"),
        "route_long_name": pd.NamedAgg(column="route_long_name", aggfunc="first"),
        "type": pd.NamedAgg(column="route_type", aggfunc="first"),
        "stops_name": pd.NamedAgg(column="stop_name", aggfunc=lambda col: col.to_list()),
        "stops_lat": pd.NamedAgg(column="stop_lat", aggfunc=lambda col: col.to_list()),
        "stops_lon": pd.NamedAgg(column="stop_lon", aggfunc=lambda col: col.to_list()),
    })
    main_trips["name"] = main_trips["route_short_name"] + " - " + main_trips["route_long_name"]
    main_trips = main_trips.drop(columns=["route_short_name", "route_long_name"])

    return {
        "public_transport": main_trips.to_dict(orient="list")
    }


class PublicTransport(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("public transport", geo_codes)
        return get_public_transport(geo_codes)

