import pandas as pd
import numpy as np
from itertools import combinations

from api.resources.common.cog import COG
from api.resources.common.get_legend_intervals import get_legend_intervals
from api.resources.common.log_stats import log_stats
from data_manager.sources.sources import get_years_for_source, get_label_link_for_source_year

from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request


source_label = "rsvero_critair"

dataset_critair = {
    "endpoint": "offer/critair",
    "is_mesh_element": True,
    "meshes": ["com", "epci"],
    "name_year": "Crit'Air",
    "years": get_years_for_source(source_label),
}

variables = ["elec", "critair1", "critair2", "critair3", "critair4", "critair5", "nc"]


def format_result(data):
    data["all"] = data[variables].sum(axis=1)
    data = data.replace({np.nan: None})
    return data


# compute legend intervals
def compute_legend_intervals():
    years = get_years_for_source(source_label)

    legend_intervals = {"com": {}, "epci": {}}

    for year in years:
        # com
        result = db_request(
            """ SELECT """ + ",".join([f"c.{v}" for v in variables]) + """
                FROM rsvero_critair AS c
                WHERE year_data = :year
            """, {"year": year}
        )
        data = pd.DataFrame(result, columns=variables, dtype=float)
        data = format_result(data)

        combinations_codes = []
        for i in range(len(variables)):
            c = combinations(variables, i+1)
            combinations_codes += [[str(a) for a in e] for e in c]

        for combination in combinations_codes:
            data[f"t_{'_'.join(combination)}"] = data[[c for c in combination]].sum(axis=1) / data["all"] * 100

        legend = data.dropna().quantile([0, .2, .4, .6, .8, 1]).round(1)
        legend_com = legend.to_dict(orient="list")

        # epci
        result = db_request(
            """ SELECT """ + ",".join([f"SUM(c.{v})" for v in variables]) + """
                FROM rsvero_critair AS c
                LEFT JOIN insee_epci_communes AS epci ON c.geo_code = epci.CODGEO
                WHERE epci.year_cog = :cog
                GROUP BY epci.EPCI
            """, {
                "cog": COG
            }
        )
        data = pd.DataFrame(result, columns=variables, dtype=float)
        data = format_result(data)

        for combination in combinations_codes:
            data[f"t_{'_'.join(combination)}"] = data[[c for c in combination]].sum(axis=1) / data["all"] * 100

        legend = data.dropna().quantile([0, .2, .4, .6, .8, 1]).round(1)
        legend_epci = legend.to_dict(orient="list")

        legend_intervals["com"][year] = legend_com
        legend_intervals["epci"][year] = legend_epci

    print("legend critair computed")
    return legend_intervals


def get_critair(geo_codes, mesh, year):
    sources = [get_label_link_for_source_year(name, year) for name in [source_label]]

    result = db_request(
        """ SELECT """ + ",".join([f"SUM(c.{v})" for v in variables]) + """
            FROM rsvero_critair AS c
            WHERE c.year_data = :year
        """,
        {
            "year": year,
        }
    )

    data = pd.DataFrame(result, columns= variables, dtype=float)
    data = format_result(data)
    references_fr = data.sum()

    if mesh == "com":
        result = db_request(
            """ SELECT """ + ",".join([f"SUM(c.{v})" for v in variables]) + """
            FROM rsvero_critair AS c
                JOIN insee_cog_communes AS cog ON c.geo_code = cog.COM
                WHERE cog.DEP IN (
                    SELECT cog2.DEP
                    FROM insee_cog_communes AS cog2
                    WHERE cog2.COM IN :geo_codes
                    AND cog2.year_cog = :cog
                  ) 
                AND c.year_data = :year
                AND cog.year_cog = :cog
            """,
            {
                "geo_codes": geo_codes,
                "year": year,
                "cog": COG
            }
        )

        data = pd.DataFrame(result, columns=variables, dtype=float)
        data = format_result(data)
        references_dep = data.sum()

        result = db_request(
            """ SELECT p.CODGEO_DES, 
                """ + ",".join(["c." + v for v in variables]) + """
            FROM rsvero_critair AS c
                JOIN insee_passage_cog AS p ON c.geo_code = p.CODGEO_INI
                WHERE p.CODGEO_DES IN :geo_codes 
                AND c.year_data = :year
                AND p.year_cog = :cog
            """,
            {
                "geo_codes": geo_codes,
                "year": year,
                "cog": COG
            }
        )

        data = pd.DataFrame(result, columns=["geo_code"] + variables)
        data = data.groupby("geo_code", as_index=False).sum()
        data = format_result(data)

        return {
            "elements": data.to_dict(orient="records"),
            "references": {
                "france": references_fr.to_dict(),
                "dep": references_dep.to_dict(),
                "territory": data.drop(columns=["geo_code"]).sum().to_dict(),
            },
            "legend": get_legend_intervals("critair", mesh, str(year)),
            "sources": sources,
            "is_mesh_element": True
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT """ + ",".join([f"SUM(c.{v})" for v in variables]) + """
                FROM rsvero_critair AS c
                JOIN insee_cog_communes AS cog ON c.geo_code = cog.COM
                WHERE cog.DEP IN (
                    SELECT cog2.DEP
                    FROM insee_cog_communes AS cog2
                    JOIN insee_epci_communes AS epci ON cog2.COM = epci.CODGEO
                    WHERE epci.EPCI IN :geo_codes
                    AND cog2.year_cog = :cog
                    AND epci.year_cog = :cog
                  ) 
                AND c.year_data = :year
                AND cog.year_cog = :cog
            """,
            {
                "geo_codes": geo_codes,
                "year": year,
                "cog": COG
            }
        )

        data = pd.DataFrame(result, columns=variables, dtype=float)
        data = format_result(data)
        references_dep = data.sum()

        result = db_request(
            """ SELECT epci.EPCI,
                """ + ",".join(["c." + v for v in variables]) + """
                FROM rsvero_critair AS c
                JOIN insee_passage_cog AS p ON c.geo_code = p.CODGEO_INI
                JOIN insee_epci_communes AS epci ON p.CODGEO_DES = epci.CODGEO
                WHERE epci.EPCI IN :geo_codes
                AND c.year_data = :year
                AND p.year_cog = :cog
                AND epci.year_cog = :cog
            """,
            {
                "geo_codes": geo_codes,
                "year": year,
                "cog": COG
            }
        )

        data = pd.DataFrame(result, columns=["geo_code"] + variables)
        data = data.groupby(by="geo_code", as_index=False).sum()
        data = format_result(data)
        data = data.sort_values(by="geo_code")

        return {
            "elements": data.to_dict(orient="records"),
            "references": {
                "france": references_fr.to_dict(),
                "dep": references_dep.to_dict(),
                "territory": data.drop(columns=["geo_code"]).sum().to_dict(),
            },
            "legend": get_legend_intervals("critair", mesh, str(year)),
            "sources": sources,
            "is_mesh_element": True
        }


class Critair(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh
        year = perimeter.year

        log_stats("critair", geo_codes, None, None)
        message_request("critair", geo_codes)
        return get_critair(geo_codes, mesh, year)


if __name__ == '__main__':
    print(get_critair(["79048"], "com", "2014"))

