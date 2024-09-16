import pandas as pd

from flask_restful import Resource

from data_manager.insee_local.source import SOURCE_DC_MOBIN
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP

from api_diago.resources.common.db_request import db_request

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_summary(geo_codes):
    variables_all = ["POP15P_CS" + str(i) for i in range(1, 9)]

    result = db_request(
        """ SELECT dc.CODGEO, dc.POP, dc.SUPERF,
                    dc.MEN,
                    dc.EMPLT, dc.ACTOCC,
                    dc.RP_VOIT1P,
                    """ + ",".join(["dc." + v for v in variables_all]) + """
            FROM insee_dossier_complet_mobin AS dc
            WHERE dc.CODGEO IN :geo_codes 
            AND dc.year_data = :year_dc
        """,
        {
            "geo_codes": geo_codes,
            "year_dc": SOURCE_DC_MOBIN,
        }
    )

    dc = pd.DataFrame(result, columns=["geo_code", "pop", "surf",
                                       "hh",
                                       "jobs_nb", "workers_nb",
                                       "hh_with_car",
                                       ] + variables_all)
    mask_high_hh_car = dc["hh"] < dc["hh_with_car"]
    dc.loc[mask_high_hh_car, "hh_with_car"] = dc.loc[mask_high_hh_car, "hh"]

    result = db_request(
        """ SELECT rsa.CODGEO,
                   rsa.beneficiaries_rsa_nb,
                   ja.jobs_applicants_ABC_nb_all, 
                   ROUND((dc.POP1519 + dc.POP2024) * neet.neet_part / 100)
            FROM observatoire_cnaf_dser_rsa_disabled AS rsa
            JOIN observatoire_dares_demandeurs_emploi AS ja ON rsa.CODGEO = ja.CODGEO
            JOIN insee_dossier_complet_mobin AS dc ON rsa.CODGEO = dc.CODGEO
            JOIN observatoire_insee_rp_neet_certificate AS neet ON rsa.CODGEO = neet.CODGEO
            WHERE rsa.CODGEO IN :geo_codes
            AND rsa.year_data = :year_rsa
            AND ja.year_data = :year_ja
            AND neet.year_data = :year_neet
        """,
        {
            "geo_codes": geo_codes,
            "year_rsa": SOURCE_CNAF_DSER,
            "year_ja": SOURCE_DARES,
            "year_neet": SOURCE_INSEE_RP,
        }
    )
    benef = pd.DataFrame(result, columns=["geo_code",
                                          "nb_beneficiaries_rsa",
                                          "jobs_applicants_ABC_nb_all",
                                          "neet_nb"])

    result = db_request(
        """ SELECT pj.CODGEO, pj.act1564prec_nb_all
            FROM observatoire_insee_rp_emploi_precaire AS pj
            WHERE pj.CODGEO IN :geo_codes 
            AND pj.year_data = :year_pj
        """,
        {
            "geo_codes": geo_codes,
            "year_pj": SOURCE_INSEE_RP,
        }
    )
    prec = pd.DataFrame(result, columns=["geo_code", "act1564prec_nb_all"])

    result = db_request(
        """ SELECT pop.CODGEO, pop.pop_variation_nb
            FROM observatoire_insee_rp_pop AS pop
            WHERE pop.CODGEO IN :geo_codes 
            AND pop.year_data = :year_rp
        """,
        {
            "geo_codes": geo_codes,
            "year_rp": SOURCE_INSEE_RP,
        }
    )
    pop_evol = pd.DataFrame(result, columns=["geo_code", "pop_variation_nb"])

    return {
        "summary": [{
            "population": int(dc["pop"].sum()),
            "density": int(dc["pop"].sum() / dc["surf"].sum()),
            "pop_evolution": int(pop_evol["pop_variation_nb"].sum()),
            "households": int(dc["hh"].sum()),
            "jobs_nb": int(dc["jobs_nb"].sum()),
            "workers_nb": int(dc["workers_nb"].sum()),
            "hh_with_car_rate": int(dc["hh_with_car"].sum() / dc["hh"].sum() * 100),
            "csp": {csp_name: int(dc[csp_name].sum()) for csp_name in variables_all},
            "jobs_applicants_ABC_nb": int(benef["jobs_applicants_ABC_nb_all"].sum()),
            "beneficiaries_rsa_nb": int(benef["nb_beneficiaries_rsa"].sum()),
            "neet_nb": int(benef["neet_nb"].sum()),
            "precarious_jobs_nb": int(prec["act1564prec_nb_all"].sum()),
        }]
    }


class Summary(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("summary", geo_codes)
        return get_summary(geo_codes)
