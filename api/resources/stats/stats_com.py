import pandas as pd
import numpy as np
import os

from api.resources.common.db_request import db_request

from flask_restful import Resource

variables = ["ip", "session_id", "geo_codes", "datetime"]


def get_requests():
    result = db_request(
        """ SELECT """ + ", ".join(variables) + """
            FROM stats_api
            WHERE name = 'geography'
            """,
        {}
    )

    requests = pd.DataFrame(result, columns=variables)
    requests = requests.replace({np.nan: None})
    requests["datetime"] = [str(d) for d in requests["datetime"]]

    return requests


def get_stats_com():
    requests = get_requests()

    mask_date = requests["datetime"] > "2024-06-18 10:50:00"
    requests = requests.loc[mask_date]

    unique_diags = requests.drop_duplicates(subset=["session_id", "geo_codes"])
    all_geo_codes = unique_diags["geo_codes"].to_list()
    all_geo_codes = [g.split("-") for g in all_geo_codes]
    geo_codes = []
    for list_g in all_geo_codes:
        for g in list_g:
            geo_codes.append(g)
    geo_codes = pd.DataFrame({"geo_codes": geo_codes})
    geo_codes["number"] = 0
    geo_codes = geo_codes.groupby(by="geo_codes", as_index=False).count()
    all_geo_codes = [f"{geocode},{number}" for geocode, number in zip(geo_codes["geo_codes"], geo_codes["number"])]

    return "geo_code,number</br>" + '</br>'.join(all_geo_codes)


class Stats(Resource):
    def get(self):
        return get_stats_com()


if __name__ == '__main__':
    print(get_stats_com())


