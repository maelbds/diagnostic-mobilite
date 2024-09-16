import pandas as pd
import numpy as np

from api.resources.common.cog import COG
from api.resources.common.log_stats import log_stats
from data_manager.sources.sources import get_years_for_source, get_label_link_for_source_year

from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request

source_label = "insee_dossier_complet"

variables_status = ["employed", "unemployed", "retired",
                    "scholars_2_5", "scholars_6_10", "scholars_11_14",
                    "scholars_15_17", "scholars_18",
                    "other"]


def get_key_figures(geo_codes, year=get_years_for_source(source_label)[-1]):
    sources = [get_label_link_for_source_year(name, year) for name in [source_label]]

    result = db_request(
        """ SELECT """ + ",".join([f"SUM(dc.{v})" for v in variables_status]) + """
            FROM insee_dossier_complet_status AS dc
            WHERE dc.year_data = :year_dc
        """,
        {
            "year_dc": year,
        }
    )

    data = pd.DataFrame(result, columns=variables_status, dtype=float).sum()
    data["population"] = data.sum()
    data["scholars"] = data[["scholars_2_5", "scholars_6_10", "scholars_11_14", "scholars_15_17", "scholars_18"]].sum()
    data = data.replace({np.nan: None}).round()
    references_fr = data

    result = db_request(
        """ SELECT dc.POP, dc.MEN, 
                   dc.EMPLT, dc.SUPERF, dc.RP_VOIT1P,
                   """ + ", ".join([f"dcs.{v}" for v in variables_status]) + """
            FROM insee_dossier_complet AS dc
            JOIN insee_dossier_complet_status AS dcs ON dc.CODGEO = dcs.CODGEO
            JOIN insee_passage_cog AS p ON dc.CODGEO = p.CODGEO_INI
            WHERE p.CODGEO_INI IN :geo_codes
            AND dc.year_data = :year_dc
            AND dcs.year_data = :year_dc
            AND p.year_cog = :cog
        """,
        {
            "geo_codes": geo_codes,
            "year_dc": year,
            "cog": COG,
        }
    )

    data = pd.DataFrame(result, columns=["population", "households",
                                         "jobs_nb", "surf", "households_with_car",
                                         ] + variables_status, dtype=float)

    data = data.sum()

    data["density"] = (data["population"] / data["surf"])
    data["jobs_concentration"] = (data["jobs_nb"] / data["employed"] * 100)
    data["motorisation_rate"] = (data["households_with_car"] / data["households"] * 100)
    data["scholars"] = data[["scholars_2_5", "scholars_6_10", "scholars_11_14", "scholars_15_17", "scholars_18"]].sum()

    data = data.replace({np.nan: None}).round()

    return {
        "key_figures": data.to_dict(),
        "references": {
            "france": references_fr.to_dict()
        },
        "sources": sources,
    }


class KeyFigures(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes

        log_stats("key_figures", geo_codes, None, None)
        message_request("key_figures", geo_codes)
        return get_key_figures(geo_codes)


if __name__ == '__main__':
    print(get_key_figures(["79048"]))
