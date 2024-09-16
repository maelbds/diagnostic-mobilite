import pandas as pd
import numpy as np

from api.resources.common.log_stats import log_stats
from api.resources.common.util_territory import get_neighbors
from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request


dataset_irve = {
    "endpoint": "offer/irve",
    "is_mesh_element": False,
    "meshes": None,
    "name_year": None,
    "years": None,
}

variables_table = ["id", "id_station_itinerance", "nom_station", "code_insee_commune", "lat", "lon",
                   "nbre_pdc", "puissance_nominale", "date_maj", "saved_on"]
variables = ["id", "id_station", "nom_station", "geo_code", "lat", "lon",
             "nbre_pdc", "puissance_nominale", "date_maj", "saved_on"]


def get_irve(geo_codes):
    influence_geocodes = get_neighbors(geo_codes)
    all_geocodes = geo_codes + influence_geocodes

    result = db_request(
        """ SELECT """ + ", ".join([v for v in variables_table]) + """
            FROM transportdatagouv_irve
            WHERE code_insee_commune IN :geo_codes 
        """,
        {
            "geo_codes": all_geocodes
        }
    )

    irve = pd.DataFrame(result, columns=variables)
    irve.drop_duplicates(subset=["nom_station", "geo_code", "lat", "lon", "nbre_pdc", "puissance_nominale", "date_maj"],
                         inplace=True)

    irve["date_maj"] = irve["date_maj"].astype(str)
    irve = irve.replace({np.nan: None})

    result = db_request(
        """ SELECT saved_on
            FROM transportdatagouv_irve
            LIMIT 1
        """, {})
    saved_on = result.scalar()

    source_data = saved_on.strftime("%m/%Y").title()
    irve.drop(columns=["saved_on"], inplace=True)

    return {
        "elements": {
            "irve": {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {
                        "coordinates": [lon, lat],
                        "geo_code": geo_code,
                        "nom_station": nom_station,
                        "nbre_pdc": nbre_pdc,
                        "puissance_nominale": puissance_nominale,
                        "date_maj": date_maj,
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    }
                } for lat, lon, geo_code, nom_station, nbre_pdc, puissance_nominale, date_maj in zip(
                    irve["lat"],
                    irve["lon"],
                    irve["geo_code"],
                    irve["nom_station"],
                    irve["nbre_pdc"],
                    irve["puissance_nominale"],
                    irve["date_maj"],
                )]
            }
        },
        "sources": [{
            "label": f"Infrastructures de Recharge pour Véhicules Électriques - IRVE (TransportDataGouv {source_data})",
            "link": "https://transport.data.gouv.fr/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques"
        }],
        "is_mesh_element": False,
    }


class IRVE(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes

        log_stats("irve", geo_codes, None, None)
        message_request("irve", geo_codes)
        return get_irve(geo_codes)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)
    print(get_irve(["79048"]))

