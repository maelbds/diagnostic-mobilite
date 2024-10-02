import pandas as pd
import numpy as np

from api.resources.common.cog import COG
from api.resources.common.get_legend_intervals import get_legend_intervals
from api.resources.common.log_stats import log_stats
from data_manager.sources.sources import get_years_for_source, get_label_link_for_source_year

from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request


source_label = "insee_dossier_complet"


def get_dataset_households_motorisation():
    return {
        "endpoint": "offer/households_motorisation",
        "is_mesh_element": True,
        "meshes": ["com", "epci"],
        "name_year": "Insee Dossier Complet",
        "years": get_years_for_source(source_label),
    }


variables = ["MEN", "RP_VOIT1P"]


def format_result(data):
    data = data.rename(columns={"MEN": "households", "RP_VOIT1P": "households_with_car"})
    data["motorisation_rate"] = [min(100, round(wc/tot * 100, 1)) if tot > 0 else None
                                 for wc, tot in zip(data["households_with_car"], data["households"])]
    data["motorisation_rate"] = data["motorisation_rate"].astype(float)
    data = data.replace({np.nan: None})
    return data


# compute legend intervals
def compute_legend_intervals():
    # com
    result = db_request(
        """ SELECT """ + ",".join([f"dc.{v}" for v in variables]) + """
            FROM insee_dossier_complet AS dc
        """, {}
    )
    data = pd.DataFrame(result, columns=variables, dtype=float)
    data = format_result(data)

    legend = data.dropna().astype(float).quantile([0, .2, .4, .6, .8, 1]).round(1)
    legend_com = legend.to_dict(orient="list")

    # epci
    result = db_request(
        """ SELECT """ + ",".join([f"SUM(dc.{v})" for v in variables]) + """
            FROM insee_dossier_complet AS dc
            LEFT JOIN insee_epci_communes AS epci ON dc.CODGEO = epci.CODGEO
            WHERE epci.year_cog = :cog
            GROUP BY epci.EPCI
        """, {
            "cog": COG
        }
    )
    data = pd.DataFrame(result, columns=variables, dtype=float)
    data = format_result(data)

    legend = data.dropna().astype(float).quantile([0, .2, .4, .6, .8, 1]).round(1)
    legend_epci = legend.to_dict(orient="list")

    print("legend hh motorisation computed")
    return {"com": legend_com, "epci": legend_epci}


def get_hh_motorisation(geo_codes, mesh, year):
    sources = [get_label_link_for_source_year(name, year) for name in [source_label]]

    result = db_request(
        """ SELECT """ + ",".join([f"SUM(dc.{v})" for v in variables]) + """
            FROM insee_dossier_complet AS dc
            WHERE dc.year_data = :year_dc
        """,
        {
            "year_dc": year,
        }
    )

    data = pd.DataFrame(result, columns=variables, dtype=float)
    data = format_result(data)
    references_fr = data.sum()

    if mesh == "com":
        result = db_request(
            """ SELECT """ + ",".join([f"SUM(dc.{v})" for v in variables]) + """
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

        data = pd.DataFrame(result, columns=variables, dtype=float)
        data = format_result(data)
        references_dep = data.sum()

        result = db_request(
            """ SELECT p.CODGEO_DES, 
                """ + ",".join(["dc." + v for v in variables]) + """
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

        data = pd.DataFrame(result, columns=["geo_code"] + variables)
        data = data.groupby("geo_code", as_index=False).sum()
        data = format_result(data)

        return {
            "elements": data.to_dict(orient="records"),
            "references": {
                "france": references_fr.to_dict(),
                "dep": references_dep.to_dict(),
                "territory": {
                    "motorisation_rate": round(data["households_with_car"].sum() / data["households"].sum() * 100, 1)
                },
            },
            "legend": get_legend_intervals("hh_motorisation", mesh),
            "sources": sources,
            "is_mesh_element": True
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT """ + ",".join([f"SUM(dc.{v})" for v in variables]) + """
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

        data = pd.DataFrame(result, columns=variables, dtype=float)
        data = format_result(data)
        references_dep = data.sum()

        result = db_request(
            """ SELECT epci.EPCI,
                """ + ",".join(["dc." + v for v in variables]) + """
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

        data = pd.DataFrame(result, columns=["geo_code"] + variables)
        data = data.groupby(by="geo_code", as_index=False).sum()
        data = format_result(data)
        data = data.sort_values(by="geo_code")

        return {
            "elements": data.to_dict(orient="records"),
            "references": {
                "france": references_fr.to_dict(),
                "dep": references_dep.to_dict(),
                "territory": {
                    "motorisation_rate": round(data["households_with_car"].sum() / data["households"].sum() * 100, 1)
                },
            },
            "legend": get_legend_intervals("hh_motorisation", mesh),
            "sources": sources,
            "is_mesh_element": True
        }


class HouseholdsMotorisation(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh
        year = perimeter.year

        log_stats("geography", geo_codes, mesh, year)
        message_request("households motorisation", geo_codes)
        return get_hh_motorisation(geo_codes, mesh, year)


if __name__ == '__main__':
    print(get_hh_motorisation(["79048"], "com", "2020"))

