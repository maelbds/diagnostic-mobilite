import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.insee_local.source import SOURCE_DC_MOBIN
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_population(geo_codes, mesh):

    variables_all = ["POP" + a for a in ["0014", "1529", "3044", "4559", "6074", "7589", "90P"]]
    variables_m = ["H" + a for a in ["0014", "1529", "3044", "4559", "6074", "7589", "90P"]]
    variables_f = ["F" + a for a in ["0014", "1529", "3044", "4559", "6074", "7589", "90P"]]

    if mesh == "com":
        result = db_request(
            """ SELECT dc.CODGEO, dc.POP, dc.POPH, dc.POPF, dc.SUPERF, 
                """ + ",".join(["dc." + v for v in variables_all + variables_m + variables_f]) + """
                FROM insee_dossier_complet_mobin AS dc
                WHERE dc.CODGEO IN :geo_codes 
                AND dc.year_data = :year_dc
            """,
            {
                "geo_codes": geo_codes,
                "year_dc": SOURCE_DC_MOBIN,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "pop_all", "pop_m", "pop_f", "surf"] +
                                            variables_all + variables_m + variables_f)
        data["ratio_fh"] = [round(pop_f/pop_m, 2) if pop_m > 0 else None for pop_f, pop_m in
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
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT epci.EPCI, dc.POP, dc.POPH, dc.POPF, dc.SUPERF, 
                """ + ",".join(["dc." + v for v in variables_all + variables_m + variables_f]) + """
                FROM insee_dossier_complet_mobin AS dc
                JOIN insee_epci_communes AS epci ON dc.CODGEO = epci.CODGEO
                WHERE epci.EPCI IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND dc.year_data = :year_dc
                AND epci.year_data = :year_epci
            """,
            {
                "geo_codes": geo_codes,
                "year_dc": SOURCE_DC_MOBIN,
                "year_epci": SOURCE_EPCI,
            }
        )

        data = pd.DataFrame(result, columns=["geo_code", "pop_all", "pop_m", "pop_f", "surf"] +
                                            variables_all + variables_m + variables_f)
        data = data.groupby(by="geo_code", as_index=False).sum()
        data["ratio_fh"] = [round(pop_f/pop_m, 2) if pop_m > 0 else None for pop_f, pop_m in
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
            "epci": data.to_dict(orient="list")
        }


class Population(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("population", geo_codes)
        return get_population(geo_codes, mesh)

