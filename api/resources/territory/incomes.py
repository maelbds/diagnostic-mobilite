import pandas as pd
import numpy as np

from api.resources.common.cog import COG
from api.resources.common.log_stats import log_stats
from data_manager.sources.sources import get_years_for_source, get_label_link_for_source_year

from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request

source_label = "insee_filosofi"

dataset_incomes = {
    "endpoint": "territory/incomes",
    "is_mesh_element": True,
    "meshes": ["com", "epci"],
    "name_year": "INSEE Filosofi",
    "years": get_years_for_source(source_label),
}

variables = ["Q2", "RD", "GI"]


def format_result(data):
    data = data.replace({np.nan: None})
    return data


def get_incomes(geo_codes, mesh, year):
    sources = [get_label_link_for_source_year(name, year) for name in [source_label]]

    result = db_request(
        """ SELECT """ + ",".join(variables) + """
            FROM insee_filosofi AS dc
            WHERE mesh = 'METROPOLE'
            AND year_data = :year
        """,
        {
            "year": year,
        }
    )

    data = pd.DataFrame(result, columns=variables, dtype=float)
    data = format_result(data)
    references_fr = data.iloc[0]

    if mesh == "com":
        result = db_request(
            """ SELECT """ + ",".join(variables) + """
                FROM insee_filosofi AS fi
                WHERE fi.CODGEO IN (
                    SELECT cog2.DEP
                    FROM insee_cog_communes AS cog2
                    WHERE cog2.COM IN :geo_codes
                    AND cog2.year_cog = :cog
                  ) 
                AND fi.mesh = 'DEP'
                AND fi.year_data = :year
            """,
            {
                "geo_codes": geo_codes,
                "year": year,
                "cog": COG
            }
        )

        data = pd.DataFrame(result, columns=variables, dtype=float)
        data = format_result(data)
        references_dep = data.iloc[0] if len(data) == 1 else None

        result = db_request(
            """ SELECT p.CODGEO_DES, 
                """ + ",".join(variables) + """
                FROM insee_filosofi AS fi
                LEFT JOIN insee_passage_cog AS p ON fi.CODGEO = p.CODGEO_INI
                WHERE p.CODGEO_DES IN :geo_codes 
                AND fi.year_data = :year
                AND p.year_cog = :cog
            """,
            {
                "geo_codes": geo_codes,
                "year": year,
                "cog": COG
            }
        )

        data = pd.DataFrame(result, columns=["geo_code"] + variables)
        data = data.drop_duplicates(subset="geo_code", keep=False)
        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = format_result(data)

        return {
            "elements": data.to_dict(orient="records"),
            "references": {
                "france": references_fr.to_dict(),
                "dep": references_dep.to_dict() if references_dep is not None else None,
            },
            "sources": sources,
            "is_mesh_element": True
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT """ + ",".join(variables) + """
                FROM insee_filosofi AS fi
                WHERE fi.CODGEO IN (
                    SELECT cog2.DEP
                    FROM insee_cog_communes AS cog2
                    JOIN insee_epci_communes AS epci ON cog2.COM = epci.CODGEO
                    WHERE epci.EPCI IN :geo_codes
                    AND cog2.year_cog = :cog
                    AND epci.year_cog = :cog
                  ) 
                AND fi.mesh = 'DEP'
                AND fi.year_data = :year
            """,
            {
                "geo_codes": geo_codes,
                "year": year,
                "cog": COG
            }
        )

        data = pd.DataFrame(result, columns=variables, dtype=float)
        data = format_result(data)
        references_dep = data.iloc[0] if len(data) == 1 else None

        result = db_request(
            """ SELECT fi.CODGEO,
                """ + ",".join(variables) + """
                FROM insee_filosofi AS fi
                WHERE fi.CODGEO IN :geo_codes
                AND (mesh = 'EPCI' OR mesh = 'EPT')
                AND fi.year_data = :year
            """,
            {
                "geo_codes": geo_codes,
                "year": year
            }
        )

        data = pd.DataFrame(result, columns=["geo_code"] + variables)
        data = format_result(data)
        data = data.sort_values(by="geo_code")

        return {
            "elements": data.to_dict(orient="records"),
            "references": {
                "france": references_fr.to_dict(),
                "dep": references_dep.to_dict() if references_dep is not None else None,
            },
            "sources": sources,
            "is_mesh_element": True
        }


class Incomes(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh
        year = perimeter.year

        log_stats("incomes", geo_codes, mesh, year)
        message_request("incomes", geo_codes)
        return get_incomes(geo_codes, mesh, year)


if __name__ == '__main__':
    print(get_incomes(["79048", "34172"], "com", "2019"))