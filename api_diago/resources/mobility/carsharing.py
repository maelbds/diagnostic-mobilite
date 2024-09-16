import pandas as pd
import numpy as np
from shapely.geometry import shape

from data_manager.transportdatagouv.source import SOURCE_BNLC

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request
from api_diago.resources.common.utilities import wkb_to_geojson


def get_rpc(geo_codes):
    result = db_request(
        """ SELECT  rpc.journey_start_insee, c1.chflieu_lat, c1.chflieu_lon, cog1.LIBELLE, 
                    rpc.journey_end_insee, c2.chflieu_lat, c2.chflieu_lon, cog2.LIBELLE, 
                    rpc.journey_distance
            FROM transportdatagouv_rpc AS rpc
            LEFT JOIN ign_commune_center AS c1 ON rpc.journey_start_insee = c1.geo_code
            LEFT JOIN insee_cog_communes AS cog1 ON rpc.journey_start_insee = cog1.COM
            LEFT JOIN ign_commune_center AS c2 ON rpc.journey_end_insee = c2.geo_code
            LEFT JOIN insee_cog_communes AS cog2 ON rpc.journey_end_insee = cog2.COM
            WHERE (rpc.journey_start_insee IN :geo_codes
                OR rpc.journey_end_insee IN :geo_codes) 
            AND rpc.journey_start_date > '2021-12-31'
            AND rpc.journey_start_date < '2023-01-01'
        """,
        {
            "geo_codes": geo_codes,
        }
    )

    data = pd.DataFrame(result, columns=["journey_start_insee", "A_lat", "A_lon", "A_name",
                                         "journey_end_insee", "B_lat", "B_lon", "B_name",
                                         "journey_distance"])
    if len(data) > 0:
        data[["journey_start_insee", "journey_end_insee"]] = [sorted([s, e]) for s, e in
                                                              zip(data["journey_start_insee"],
                                                                  data["journey_end_insee"])]

        data = data.groupby(by=["journey_start_insee", "journey_end_insee"], as_index=False).agg(**{
            "number": pd.NamedAgg("journey_distance", aggfunc="count"),
            "A_lat": pd.NamedAgg("A_lat", aggfunc="first"),
            "A_lon": pd.NamedAgg("A_lon", aggfunc="first"),
            "A_name": pd.NamedAgg("A_name", aggfunc="first"),
            "B_lat": pd.NamedAgg("B_lat", aggfunc="first"),
            "B_lon": pd.NamedAgg("B_lon", aggfunc="first"),
            "B_name": pd.NamedAgg("B_name", aggfunc="first"),
        })

        data["number"] = (data["number"] / 12).round()
        mask_low_frequency = data["number"] < 10
        data = data[~mask_low_frequency]

        data["A_center"] = [[lat, lon] for lat, lon in zip(data["A_lat"], data["A_lon"])]
        data["B_center"] = [[lat, lon] for lat, lon in zip(data["B_lat"], data["B_lon"])]
        data.drop(columns=["A_lat", "A_lon", "B_lat", "B_lon"], inplace=True)
        data["mesh"] = "com"

    rpc_flows_com = data

    result = db_request(
        """ SELECT  epci1.EPCI, o1.outline, e1.LIBEPCI, 
                    epci2.EPCI, o2.outline, e2.LIBEPCI,  
                    rpc.journey_distance
            FROM transportdatagouv_rpc AS rpc

            LEFT JOIN insee_epci_communes AS epci1 ON rpc.journey_start_insee = epci1.CODGEO
            LEFT JOIN ign_epci_outline AS o1 ON epci1.EPCI = o1.epci_siren
            LEFT JOIN insee_epci AS e1 ON epci1.EPCI = e1.EPCI

            LEFT JOIN insee_epci_communes AS epci2 ON rpc.journey_end_insee = epci2.CODGEO
            LEFT JOIN ign_epci_outline AS o2 ON epci2.EPCI = o2.epci_siren
            LEFT JOIN insee_epci AS e2 ON epci2.EPCI = e2.EPCI

            WHERE (rpc.journey_start_insee IN :geo_codes
                OR rpc.journey_end_insee IN :geo_codes)
            AND rpc.journey_start_date > '2021-12-31'
            AND rpc.journey_start_date < '2023-01-01'
        """,
        {
            "geo_codes": geo_codes,
        }
    )
    data = pd.DataFrame(result, columns=["journey_start_insee", "A_outline", "A_name",
                                         "journey_end_insee", "B_outline", "B_name",
                                         "journey_distance"])
    data = data.dropna(subset=["journey_start_insee", "journey_end_insee"])

    if len(data) > 0:
        data[["journey_start_insee", "journey_end_insee"]] = [sorted([s, e]) for s, e in
                                                              zip(data["journey_start_insee"],
                                                                  data["journey_end_insee"])]

        data = data.groupby(by=["journey_start_insee", "journey_end_insee"], as_index=False).agg(**{
            "number": pd.NamedAgg("journey_distance", aggfunc="count"),
            "A_outline": pd.NamedAgg("A_outline", aggfunc="first"),
            "A_name": pd.NamedAgg("A_name", aggfunc="first"),
            "B_outline": pd.NamedAgg("B_outline", aggfunc="first"),
            "B_name": pd.NamedAgg("B_name", aggfunc="first"),
        })
        data["number"] = (data["number"] / 12).round()
        mask_low_frequency = data["number"] < 10
        data = data[~mask_low_frequency]

        data["A_outline"] = [wkb_to_geojson(outline) for outline in data["A_outline"]]
        data["B_outline"] = [wkb_to_geojson(outline) for outline in data["B_outline"]]
        data["A_center"] = [list(reversed(shape(outline).centroid.coords[0])) for outline in data["A_outline"]]
        data["B_center"] = [list(reversed(shape(outline).centroid.coords[0])) for outline in data["B_outline"]]
        data.drop(columns=["A_outline", "B_outline"], inplace=True)
        data["mesh"] = "epci"

    rpc_flows_epci = data

    rpc_flows = pd.concat([rpc_flows_epci, rpc_flows_com])

    return {
        "rpc_flows": rpc_flows.to_dict(orient="list")
    }


def get_bnlc(geo_codes):
    result = db_request(
        """ SELECT id_lieu, nom_lieu, type, insee, Ylat, Xlong, 
                   nbre_pl, nbre_pmr, date_maj
            FROM transportdatagouv_bnlc 
            WHERE insee IN :geo_codes 
            AND source = :source
        """,
        {
            "geo_codes": geo_codes,
            "source": SOURCE_BNLC
        }
    )

    bnlc = pd.DataFrame(result, columns=["id", "name", "type", "geo_code", "lat", "lon",
                                         "nbre_pl", "nbre_pmr", "date_maj"])

    bnlc["nbre_pl"] = bnlc["nbre_pl"].replace({np.nan: None})
    bnlc["nbre_pmr"] = bnlc["nbre_pmr"].replace({np.nan: None})
    bnlc["date_maj"] = bnlc["date_maj"].astype(str)

    return {
        "bnlc": bnlc.to_dict(orient="list")
    }


class RPC(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("rpc", geo_codes)
        return get_rpc(geo_codes)


class BNLC(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("bnlc", geo_codes)
        return get_bnlc(geo_codes)

