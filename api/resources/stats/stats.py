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


def get_stats():
    requests = get_requests()

    mask_date = requests["datetime"] > "2024-06-18 10:50:00"
    requests = requests.loc[mask_date]

    total_nb_requests = len(requests)
    last_request = requests["datetime"].max()

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
    geo_codes_table = geo_codes.sort_values(by="number", ascending=False).to_html(max_rows=30)
    all_geo_codes = [f"{geocode},{number}" for geocode, number in zip(geo_codes["geo_codes"], geo_codes["number"])]
    #geo_codes.to_csv("stats_com.csv", index=False)

    nb_unique_diags = len(unique_diags)
    nb_unique_users = len(requests.drop_duplicates(subset="session_id"))

    unique_diags_table = unique_diags.groupby("session_id").agg(**{
        "ip": pd.NamedAgg(column="ip", aggfunc="count"),
        "geo_codes": pd.NamedAgg(column="geo_codes", aggfunc="sum"),
        "min_date": pd.NamedAgg(column="datetime", aggfunc="min"),
        "max_date": pd.NamedAgg(column="datetime", aggfunc="max"),
    }).sort_values(by="ip", ascending=False).to_html(max_rows=50)

    return f"""
    <h1>Statistiques Diagnostic Mobilité</h1>
    <p><i>Depuis le lancement (18/06)</i></p>
    <p>Nombre total de requêtes : <b>{total_nb_requests}</b></p>
    <p>Nombre total d'utilisateurs uniques : <b>{nb_unique_users}</b></p>
    <p>Nombre total de diagnostics : <b>{nb_unique_diags}</b></p>
    <p>- soit {round(nb_unique_diags/nb_unique_users, 2)} diagnostics/utilisateur</p>
    
    <p></p>
    <p>Dernière requête le : {last_request}</p>
    <p><u>Dernières requêtes</u></p>
    
    {requests.sort_values(by="datetime", ascending=False).iloc[:20].to_html()}
    
    <p><u>Principaux utilisateurs</u></p>
    {unique_diags_table}
    """


class Stats(Resource):
    def get(self):
        return get_stats()


if __name__ == '__main__':
    print(get_stats())


