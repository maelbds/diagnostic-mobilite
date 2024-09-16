import pandas as pd

from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.log_stats import log_stats
from api.resources.common.schema_request import context_get_request


dataset_public_transport = {
    "endpoint": "offer/public_transport",
    "is_mesh_element": False,
    "meshes": None,
    "name_year": "Transport Data Gouv",
    "years": None,
}


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

    stops = main_trips[["route_id", "route_type", "stop_name", "stop_lat", "stop_lon"]]
    stops["route_name"] = main_trips["route_short_name"] + " - " + main_trips["route_long_name"]

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

    stops = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {
                "route_id": route_id,
                "route_type": route_type,
                "route_name": route_name,
                "stop_name": name.title(),
            },
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            }
        } for route_id, route_type, route_name, name, lat, lon in zip(
            stops["route_id"],
            stops["route_type"],
            stops["route_name"],
            stops["stop_name"],
            stops["stop_lat"],
            stops["stop_lon"],
        )]
    }

    routes = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {
                "route_id": id,
                "route_type": type,
                "route_name": name,
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [[lon, lat] for lon, lat in zip(stop_lon, stop_lat)]
            }
        } for id, type, name, stop_lat, stop_lon in zip(
            main_trips["route_id"],
            main_trips["type"],
            main_trips["name"],
            main_trips["stops_lat"],
            main_trips["stops_lon"],
        )]
    }

    return {
        "elements": {
            "stops": stops,
            "routes": routes
        },
        "sources": {
            "label": "Point d’Accès National aux données de transport (TransportDataGouv 2024)",
            "link": "https://transport.data.gouv.fr/"
        },
        "is_mesh_element": False,
    }


class PublicTransport(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes

        log_stats("pubic transport", geo_codes, None, None)
        message_request("public transport", geo_codes)
        return get_public_transport(geo_codes)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)
    get_public_transport(["75056"])
