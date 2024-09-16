import pandas as pd
import numpy as np
from difflib import get_close_matches

from data_manager.insee_general.source import SOURCE_EPCI

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import beneficaries_adresses_request


def convert_name(name):
    name = name.upper()
    name = name.replace('-', ' ').replace('\'', ' ').replace("CEDEX", "").replace("  ", " ")
    name = name.replace('SAINT', 'ST')
    return name


def postal_code_to_geo_code(postal_code, name):
    name = convert_name(name)

    result = db_request(
        """ SELECT CODGEO, arr.geo_code_city, LIBELLE
            FROM la_poste_code_postal AS lp
            LEFT JOIN insee_arrondissements AS arr ON lp.CODGEO = arr.geo_code_district
            WHERE code_postal = :code_postal
        """,
        {
            "code_postal": postal_code
        }
    )
    communes = pd.DataFrame(result, columns=["geo_code", "geo_code_city", "name"])
    mask_district = ~communes["geo_code_city"].isna()
    communes.loc[mask_district, "geo_code"] = communes.loc[mask_district, "geo_code_city"]

    if len(communes)>1:
        close_matches = get_close_matches(name, communes["name"].to_list(), 1)
        if len(close_matches) > 0:
            matching_commune = get_close_matches(name, communes["name"].to_list(), 1)[0]
            return communes[communes["name"] == matching_commune]["geo_code"].iloc[0]
        else:
            return None

    elif len(communes)==1:
        return communes["geo_code"].iloc[0]
    else:
        return None


def get_beneficiaries_insee(postal_codes, names):
    communes = pd.DataFrame({
        "postal_code": postal_codes,
        "name": names,
    })
    communes["postal_code"] = ["0" + c if len(c) == 4 else c for c in communes["postal_code"]]

    communes["geo_code"] = [postal_code_to_geo_code(postal_code, name)
                            for postal_code, name in zip(communes["postal_code"], communes["name"])]

    result = db_request(
        """ SELECT CODGEO, EPCI
            FROM insee_epci_communes
            WHERE CODGEO IN :geo_codes
            AND year_cog = :year_epci
        """,
        {
            "geo_codes": [g for g in communes["geo_code"] if g is not None],
            "year_epci": SOURCE_EPCI
        }
    )
    epci = pd.DataFrame(result, columns=["geo_code", "epci"])

    communes = pd.merge(communes, epci, on="geo_code", how="left").replace({np.nan: None})

    return {
        "communes": communes["geo_code"].to_list(),
        "epci": communes["epci"].to_list(),
    }


class BeneficiariesInsee(Resource):
    def post(self):
        perimeter = beneficaries_adresses_request.parse()
        postal_codes = perimeter.postal_codes
        names = perimeter.names

        message_request("beneficiaries", postal_codes)
        return get_beneficiaries_insee(postal_codes, names)

