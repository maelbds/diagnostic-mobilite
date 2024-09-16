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

dataset_population = {
    "endpoint": "territory/population",
    "is_mesh_element": True,
    "meshes": ["com", "epci"],
    "name_year": "Insee Dossier Complet",
    "years": get_years_for_source(source_label),
}

ages = ["0014", "1529", "3044", "4559", "6074", "7589", "90P"]
variables_all = ["POP" + a for a in ages]
variables_m = ["H" + a for a in ages]
variables_f = ["F" + a for a in ages]


# compute legend intervals
def compute_legend_intervals():
    # com

    result = db_request(
        """ SELECT dc.POP, dc.POPH, dc.POPF, dc.SUPERF, 
            """ + ",".join([f"dc.{v}" for v in variables_all + variables_m + variables_f]) + """
            FROM insee_dossier_complet AS dc
        """, {}
    )

    data = pd.DataFrame(result, columns=["pop_all", "pop_m", "pop_f", "surf"] +
                                        variables_all + variables_m + variables_f, dtype=float)
    data["ratio_fh"] = [round(pop_f / pop_m, 2) if pop_m > 0 else None for pop_f, pop_m in
                        zip(data["pop_f"], data["pop_m"])]
    data["density"] = [round(pop / surf, 2) if surf > 0 else None for pop, surf in
                       zip(data["pop_all"], data["surf"])]
    data["H_all"] = data[variables_m].sum(axis=1)
    data["F_all"] = data[variables_f].sum(axis=1)
    data["POP_all"] = data[variables_all].sum(axis=1)
    data = data.rename(
        columns=lambda name: name.replace("H", "m").replace("F", "f").replace("POP", "all").replace("0014", "14"))

    combinations_ages = []
    for i in range(len(ages)):
        c = combinations(ages, i+1)
        combinations_ages += [[a.replace("0014", "14") for a in e] for e in c]

    for combination in combinations_ages:
        data[f"r_all_{'_'.join(combination)}"] = data[[f"all{c}" for c in combination]].sum(axis=1) / data["pop_all"] * 100

    legend = data.dropna().quantile([0, .2, .4, .6, .8, 1]).round(1)
    legend_com = legend.to_dict(orient="list")

    # epci

    result = db_request(
        """ SELECT SUM(dc.POP), SUM(dc.POPH), SUM(dc.POPF), SUM(dc.SUPERF), 
            """ + ",".join([f"SUM(dc.{v})" for v in variables_all + variables_m + variables_f]) + """
            FROM insee_dossier_complet AS dc
            LEFT JOIN insee_epci_communes AS epci ON dc.CODGEO = epci.CODGEO
            WHERE epci.year_cog = :cog
            GROUP BY epci.EPCI
        """, {
            "cog": COG
        }
    )

    data = pd.DataFrame(result, columns=["pop_all", "pop_m", "pop_f", "surf"] +
                                        variables_all + variables_m + variables_f, dtype=float)
    data["ratio_fh"] = [round(pop_f / pop_m, 2) if pop_m > 0 else None for pop_f, pop_m in
                        zip(data["pop_f"], data["pop_m"])]
    data["density"] = [round(pop / surf, 2) if surf > 0 else None for pop, surf in
                       zip(data["pop_all"], data["surf"])]
    data["H_all"] = data[variables_m].sum(axis=1)
    data["F_all"] = data[variables_f].sum(axis=1)
    data["POP_all"] = data[variables_all].sum(axis=1)
    data = data.rename(
        columns=lambda name: name.replace("H", "m").replace("F", "f").replace("POP", "all").replace("0014", "14"))

    combinations_ages = []
    for i in range(len(ages)):
        c = combinations(ages, i+1)
        combinations_ages += [[a.replace("0014", "14") for a in e] for e in c]

    for combination in combinations_ages:
        data[f"r_all_{'_'.join(combination)}"] = data[[f"all{c}" for c in combination]].sum(axis=1) / data["pop_all"] * 100

    legend = data.dropna().quantile([0, .2, .4, .6, .8, 1]).round(1)
    legend_epci = legend.to_dict(orient="list")

    print("legend population computed")
    return {"com": legend_com, "epci": legend_epci}


def get_population(geo_codes, mesh, year):
    sources = [get_label_link_for_source_year(name, year) for name in [source_label]]

    result = db_request(
        """ SELECT SUM(dc.POP), SUM(dc.POPH), SUM(dc.POPF), SUM(dc.SUPERF), 
            """ + ",".join([f"SUM(dc.{v})" for v in variables_all + variables_m + variables_f]) + """
            FROM insee_dossier_complet AS dc
            WHERE dc.year_data = :year_dc
        """,
        {
            "year_dc": year,
        }
    )

    data = pd.DataFrame(result, columns=["pop_all", "pop_m", "pop_f", "surf"] +
                                        variables_all + variables_m + variables_f, dtype=float)
    data["ratio_fh"] = [round(pop_f / pop_m, 2) if pop_m > 0 else None for pop_f, pop_m in
                        zip(data["pop_f"], data["pop_m"])]
    data["density"] = [round(pop / surf, 2) if surf > 0 else None for pop, surf in
                       zip(data["pop_all"], data["surf"])]
    data["H_all"] = data[variables_m].sum(axis=1)
    data["F_all"] = data[variables_f].sum(axis=1)
    data["POP_all"] = data[variables_all].sum(axis=1)
    data = data.rename(
        columns=lambda name: name.replace("H", "m").replace("F", "f").replace("POP", "all").replace("0014", "14"))
    data = data.replace({np.nan: None}).round(1)
    references_fr = data.sum()

    if mesh == "com":
        result = db_request(
            """ SELECT SUM(dc.POP), SUM(dc.POPH), SUM(dc.POPF), SUM(dc.SUPERF), 
                """ + ",".join([f"SUM(dc.{v})" for v in variables_all + variables_m + variables_f]) + """
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

        data = pd.DataFrame(result, columns=["pop_all", "pop_m", "pop_f", "surf"] +
                                            variables_all + variables_m + variables_f, dtype=float)
        data["ratio_fh"] = [round(pop_f / pop_m, 2) if pop_m > 0 else None for pop_f, pop_m in
                            zip(data["pop_f"], data["pop_m"])]
        data["density"] = [round(pop / surf, 2) if surf > 0 else None for pop, surf in
                           zip(data["pop_all"], data["surf"])]
        data["H_all"] = data[variables_m].sum(axis=1)
        data["F_all"] = data[variables_f].sum(axis=1)
        data["POP_all"] = data[variables_all].sum(axis=1)
        data = data.rename(
            columns=lambda name: name.replace("H", "m").replace("F", "f").replace("POP", "all").replace("0014", "14"))
        data = data.replace({np.nan: None}).round(1)
        references_dep = data.sum()

        result = db_request(
            """ SELECT p.CODGEO_DES, dc.POP, dc.POPH, dc.POPF, dc.SUPERF, 
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

        data = pd.DataFrame(result, columns=["geo_code", "pop_all", "pop_m", "pop_f", "surf"] +
                                            variables_all + variables_m + variables_f)

        data = data.groupby("geo_code", as_index=False).sum()

        data["ratio_fh"] = [round(pop_f / pop_m, 2) if pop_m > 0 else None for pop_f, pop_m in
                            zip(data["pop_f"], data["pop_m"])]
        data["density"] = [round(pop / surf, 2) if surf > 0 else None for pop, surf in
                           zip(data["pop_all"], data["surf"])]
        data["H_all"] = data[variables_m].sum(axis=1)
        data["F_all"] = data[variables_f].sum(axis=1)
        data["POP_all"] = data[variables_all].sum(axis=1)
        data = data.rename(
            columns=lambda name: name.replace("H", "m").replace("F", "f").replace("POP", "all").replace("0014", "14"))
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: None}).round(1)

        return {
            "elements": data.to_dict(orient="records"),
            "references": {
                "france": references_fr.to_dict(),
                "dep": references_dep.to_dict(),
                "territory": data.drop(columns=["geo_code"]).sum().to_dict(),
            },
            "legend": get_legend_intervals("population", mesh),
            "sources": sources,
            "is_mesh_element": True
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT SUM(dc.POP), SUM(dc.POPH), SUM(dc.POPF), SUM(dc.SUPERF), 
                """ + ",".join([f"SUM(dc.{v})" for v in variables_all + variables_m + variables_f]) + """
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

        data = pd.DataFrame(result, columns=["pop_all", "pop_m", "pop_f", "surf"] +
                                            variables_all + variables_m + variables_f, dtype=float)
        data["ratio_fh"] = [round(pop_f / pop_m, 2) if pop_m > 0 else None for pop_f, pop_m in
                            zip(data["pop_f"], data["pop_m"])]
        data["density"] = [round(pop / surf, 2) if surf > 0 else None for pop, surf in
                           zip(data["pop_all"], data["surf"])]
        data["H_all"] = data[variables_m].sum(axis=1)
        data["F_all"] = data[variables_f].sum(axis=1)
        data["POP_all"] = data[variables_all].sum(axis=1)
        data = data.rename(
            columns=lambda name: name.replace("H", "m").replace("F", "f").replace("POP", "all").replace("0014", "14"))
        data = data.replace({np.nan: None}).round(1)
        references_dep = data.sum()

        result = db_request(
            """ SELECT epci.EPCI, p.CODGEO_DES, dc.POP, dc.POPH, dc.POPF, dc.SUPERF, 
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

        data = pd.DataFrame(result, columns=["geo_code", "geo_code2", "pop_all", "pop_m", "pop_f", "surf"] +
                                            variables_all + variables_m + variables_f)
        data = data.groupby(by="geo_code", as_index=False).sum()
        data["ratio_fh"] = [round(pop_f / pop_m, 2) if pop_m > 0 else None for pop_f, pop_m in
                            zip(data["pop_f"], data["pop_m"])]
        data["density"] = [round(pop / surf, 2) if surf > 0 else None for pop, surf in
                           zip(data["pop_all"], data["surf"])]
        data["H_all"] = data[variables_m].sum(axis=1)
        data["F_all"] = data[variables_f].sum(axis=1)
        data["POP_all"] = data[variables_all].sum(axis=1)
        data = data.rename(
            columns=lambda name: name.replace("H", "m").replace("F", "f").replace("POP", "all").replace("0014", "14"))
        data = data.replace({np.nan: None}).round(1)
        data = data.sort_values(by="geo_code")

        return {
            "elements": data.to_dict(orient="records"),
            "references": {
                "france": references_fr.to_dict(),
                "dep": references_dep.to_dict(),
                "territory": data.drop(columns=["geo_code"]).sum().to_dict(),
            },
            "legend": get_legend_intervals("population", mesh),
            "sources": sources,
            "is_mesh_element": True
        }


class Population(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh
        year = perimeter.year

        log_stats("population", geo_codes, mesh, year)
        message_request("population", geo_codes)
        return get_population(geo_codes, mesh, year)
