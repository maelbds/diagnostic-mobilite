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


source_label = "insee_dossier_complet"


def get_dataset_pop_csp():
    return {
        "endpoint": "territory/pop_csp",
        "is_mesh_element": True,
        "meshes": ["com", "epci"],
        "name_year": "Insee Dossier Complet",
        "years": get_years_for_source(source_label),
    }


csp_codes = range(1, 9)
variables_all = ["POP15P_CS" + str(i) for i in csp_codes]
variables_m = ["H15P_CS" + str(i) for i in csp_codes]
variables_f = ["F15P_CS" + str(i) for i in csp_codes]


def format_result(data):
    data["POP15P"] = data[variables_all].sum(axis=1)
    data["H15P"] = data[variables_m].sum(axis=1)
    data["F15P"] = data[variables_f].sum(axis=1)
    data = data.replace({np.nan: None}).round(1)
    data = data.rename(columns=lambda name: name.replace("POP", "all").replace("H", "m").replace("F", "f"))
    return data


# compute legend intervals
def compute_legend_intervals():
    # com

    result = db_request(
        """ SELECT """ + ",".join([f"dc.{v}" for v in variables_all + variables_m + variables_f]) + """
            FROM insee_dossier_complet AS dc
        """, {}
    )
    data = pd.DataFrame(result, columns=variables_all + variables_m + variables_f, dtype=float)
    data = format_result(data)

    combinations_csp_codes = []
    for i in range(len(csp_codes)):
        c = combinations(csp_codes, i+1)
        combinations_csp_codes += [[str(a) for a in e] for e in c]

    for combination in combinations_csp_codes:
        data[f"all15P_CS_{'_'.join(combination)}"] = data[[f"all15P_CS{c}" for c in combination]].sum(axis=1) / data["all15P"] * 100
        data[f"m15P_CS_{'_'.join(combination)}"] = data[[f"m15P_CS{c}" for c in combination]].sum(axis=1) / data["m15P"] * 100
        data[f"f15P_CS_{'_'.join(combination)}"] = data[[f"f15P_CS{c}" for c in combination]].sum(axis=1) / data["f15P"] * 100

    legend = data.dropna().quantile([0, .2, .4, .6, .8, 1]).round(1)
    legend_com = legend.to_dict(orient="list")

    # epci
    result = db_request(
        """ SELECT """ + ",".join([f"SUM(dc.{v})" for v in variables_all + variables_m + variables_f]) + """
            FROM insee_dossier_complet AS dc
            LEFT JOIN insee_epci_communes AS epci ON dc.CODGEO = epci.CODGEO
            WHERE epci.year_cog = :cog
            GROUP BY epci.EPCI
        """, {
            "cog": COG
        }
    )
    data = pd.DataFrame(result, columns=variables_all + variables_m + variables_f, dtype=float)
    data = format_result(data)

    for combination in combinations_csp_codes:
        data[f"all15P_CS_{'_'.join(combination)}"] = data[[f"all15P_CS{c}" for c in combination]].sum(axis=1) / data["all15P"] * 100
        data[f"m15P_CS_{'_'.join(combination)}"] = data[[f"m15P_CS{c}" for c in combination]].sum(axis=1) / data["m15P"] * 100
        data[f"f15P_CS_{'_'.join(combination)}"] = data[[f"f15P_CS{c}" for c in combination]].sum(axis=1) / data["f15P"] * 100

    legend = data.dropna().quantile([0, .2, .4, .6, .8, 1]).round(1)
    legend_epci = legend.to_dict(orient="list")

    print("legend pop_csp computed")
    return {"com": legend_com, "epci": legend_epci}


def get_csp(geo_codes, mesh, year):
    sources = [get_label_link_for_source_year(name, year) for name in [source_label]]

    result = db_request(
        """ SELECT """ + ",".join([f"SUM(dc.{v})" for v in variables_all + variables_m + variables_f]) + """
            FROM insee_dossier_complet AS dc
            WHERE dc.year_data = :year_dc
        """,
        {
            "year_dc": year,
        }
    )

    data = pd.DataFrame(result, columns= variables_all + variables_m + variables_f, dtype=float)
    data = format_result(data)
    references_fr = data.sum()

    if mesh == "com":
        result = db_request(
            """ SELECT """ + ",".join([f"SUM(dc.{v})" for v in variables_all + variables_m + variables_f]) + """
                FROM insee_dossier_complet AS dc
                JOIN insee_cog_communes AS cog ON dc.CODGEO = cog.COM
                WHERE cog.DEP IN (
                    SELECT cog2.DEP
                    FROM insee_cog_communes AS cog2
                    WHERE cog2.COM IN :geo_codes
                    AND cog2.year_cog = :cog
                  ) 
                AND dc.year_data = :year_dc
                AND cog.year_cog = :cog
            """,
            {
                "geo_codes": geo_codes,
                "year_dc": year,
                "cog": COG
            }
        )

        data = pd.DataFrame(result, columns=variables_all + variables_m + variables_f, dtype=float)
        data = format_result(data)
        references_dep = data.sum()

        result = db_request(
            """ SELECT p.CODGEO_DES, 
                """ + ",".join(["dc." + v for v in variables_all + variables_m + variables_f]) + """
                FROM insee_dossier_complet AS dc
                JOIN insee_passage_cog AS p ON dc.CODGEO = p.CODGEO_INI
                WHERE p.CODGEO_DES IN :geo_codes 
                AND dc.year_data = :year_dc
                AND p.year_cog = :cog
            """,
            {
                "geo_codes": geo_codes,
                "year_dc": year,
                "cog": COG
            }
        )

        data = pd.DataFrame(result, columns=["geo_code"] + variables_all + variables_m + variables_f)
        data = data.groupby("geo_code", as_index=False).sum()
        data = format_result(data)

        return {
            "elements": data.to_dict(orient="records"),
            "references": {
                "france": references_fr.to_dict(),
                "dep": references_dep.to_dict(),
                "territory": data.drop(columns=["geo_code"]).sum().to_dict(),
            },
            "legend": get_legend_intervals("pop_csp", mesh),
            "sources": sources,
            "is_mesh_element": True
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT """ + ",".join([f"SUM(dc.{v})" for v in variables_all + variables_m + variables_f]) + """
                FROM insee_dossier_complet AS dc
                JOIN insee_cog_communes AS cog ON dc.CODGEO = cog.COM
                WHERE cog.DEP IN (
                    SELECT cog2.DEP
                    FROM insee_cog_communes AS cog2
                    JOIN insee_epci_communes AS epci ON cog2.COM = epci.CODGEO
                    WHERE epci.EPCI IN :geo_codes
                    AND cog2.year_cog = :cog
                    AND epci.year_cog = :cog
                  ) 
                AND dc.year_data = :year_dc
                AND cog.year_cog = :cog
            """,
            {
                "geo_codes": geo_codes,
                "year_dc": year,
                "cog": COG
            }
        )

        data = pd.DataFrame(result, columns=variables_all + variables_m + variables_f, dtype=float)
        data = format_result(data)
        references_dep = data.sum()

        result = db_request(
            """ SELECT epci.EPCI,
                """ + ",".join(["dc." + v for v in variables_all + variables_m + variables_f]) + """
                FROM insee_dossier_complet AS dc
                JOIN insee_passage_cog AS p ON dc.CODGEO = p.CODGEO_INI
                JOIN insee_epci_communes AS epci ON p.CODGEO_DES = epci.CODGEO
                WHERE epci.EPCI IN :geo_codes
                AND dc.year_data = :year_dc
                AND p.year_cog = :cog
                AND epci.year_cog = :cog
            """,
            {
                "geo_codes": geo_codes,
                "year_dc": year,
                "cog": COG
            }
        )

        data = pd.DataFrame(result, columns=["geo_code"] + variables_all + variables_m + variables_f)
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
            "legend": get_legend_intervals("pop_csp", mesh),
            "sources": sources,
            "is_mesh_element": True
        }


class Pop_CSP(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh
        year = perimeter.year

        log_stats("pop_csp", geo_codes, mesh, year)
        message_request("pop_csp", geo_codes)
        return get_csp(geo_codes, mesh, year)
