import pandas as pd
import numpy as np

from data_manager.insee_general.source import SOURCE_EPCI
from data_manager.observatoire_territoire.source import SOURCE_CNAF_DSER, SOURCE_DARES, SOURCE_INSEE_RP

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request


def get_beneficiaries(geo_codes, mesh):
    if mesh == "com":
        result = db_request(
            """ SELECT rsa.CODGEO,
                       rsa.beneficiaries_rsa_nb, rsa.beneficiaries_rsa_part,

                       rsa.beneficiaries_disabled_nb, (dc.POP2024 + dc.POP2539 + dc.POP4054 + dc.POP5564 + dc.POP6579 + dc.POP80P),

                       ja.jobs_applicants_ABC_nb_all, (dc.POP1519 + dc.POP2024 + dc.POP2539 + dc.POP4054 + dc.POP5564),

                       ROUND(ja.jobs_applicants_ABC_nb_all * ja.jobs_applicants_ABC_part_m25y / 100), (dc.POP1519 + dc.POP2024),

                       ROUND((dc.POP1519 + dc.POP2024) * neet.neet_part / 100), neet.neet_part,

                       ROUND(dc.POP2024 * neet.no_certificate_part / 100), neet.no_certificate_part

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

        data = pd.DataFrame(result, columns=["geo_code",
                                             "nb_beneficiaries_rsa", "part_beneficiaries_rsa",
                                             "beneficiaries_disabled_nb", "pop_20p",
                                             "jobs_applicants_ABC_nb_all", "pop_1564",
                                             "jobs_applicants_ABC_nb_m25", "pop_1524",
                                             "neet_nb", "neet_part",
                                             "no_certificate_nb", "no_certificate_part"
                                             ])
        data["beneficiaries_disabled_part"] = ((data["beneficiaries_disabled_nb"] / data["pop_20p"]) * 100).round(1)

        data = pd.merge(pd.DataFrame({"geo_code": geo_codes}), data, on="geo_code", how="left")
        data = data.replace({np.nan: None})

        data["jobs_applicants_ABC_part_all"] = [round(ja / pop * 100, 1) if pop is not None and pop > 0 else 0 for
                                                ja, pop in zip(data["jobs_applicants_ABC_nb_all"], data["pop_1564"])]
        data["jobs_applicants_ABC_part_m25"] = [round(ja / pop * 100, 1) if pop is not None and pop > 0 else 0 for
                                                ja, pop in zip(data["jobs_applicants_ABC_nb_m25"], data["pop_1524"])]

        data.drop(columns=["pop_1564", "pop_1524"], inplace=True)

        return {
            "com": data.to_dict(orient="list")
        }

    elif mesh == "epci":
        result = db_request(
            """ SELECT epci.EPCI,

                    rsa.beneficiaries_rsa_nb, rsa.beneficiaries_rsa_part,

                    rsa.beneficiaries_disabled_nb, (dc.POP2024 + dc.POP2539 + dc.POP4054 + dc.POP5564 + dc.POP6579 + dc.POP80P),

                    ja.jobs_applicants_ABC_nb_all, (dc.POP1519 + dc.POP2024 + dc.POP2539 + dc.POP4054 + dc.POP5564),

                    ROUND(ja.jobs_applicants_ABC_nb_all * ja.jobs_applicants_ABC_part_m25y / 100), (dc.POP1519 + dc.POP2024),

                    ROUND((dc.POP1519 + dc.POP2024) * neet.neet_part / 100), neet.neet_part,

                    ROUND(dc.POP2024 * neet.no_certificate_part / 100), neet.no_certificate_part

                FROM observatoire_cnaf_dser_rsa_disabled AS rsa
                JOIN observatoire_dares_demandeurs_emploi AS ja ON rsa.CODGEO = ja.CODGEO
                JOIN insee_dossier_complet_mobin AS dc ON rsa.CODGEO = dc.CODGEO
                JOIN observatoire_insee_rp_neet_certificate AS neet ON rsa.CODGEO = neet.CODGEO
                JOIN insee_epci_communes AS epci ON rsa.CODGEO = epci.CODGEO
                WHERE epci.EPCI IN (
                    SELECT epci2.EPCI
                    FROM insee_epci_communes AS epci2
                    WHERE epci2.CODGEO IN :geo_codes
                    AND epci2.year_data = :year_epci
                  ) 
                AND rsa.year_data = :year_rsa
                AND ja.year_data = :year_ja
                AND neet.year_data = :year_neet
                AND epci.year_data = :year_epci
            """,
            {
                "geo_codes": geo_codes,
                "year_rsa": SOURCE_CNAF_DSER,
                "year_ja": SOURCE_DARES,
                "year_neet": SOURCE_INSEE_RP,
                "year_epci": SOURCE_EPCI,
            }
        )

        def agg_func(df):
            return pd.Series({
                "nb_beneficiaries_rsa": df["nb_beneficiaries_rsa"].sum(),
                "part_beneficiaries_rsa": df["nb_beneficiaries_rsa"].sum() / (
                            df["nb_beneficiaries_rsa"] / df["part_beneficiaries_rsa"]).sum(),

                "beneficiaries_disabled_nb": df["beneficiaries_disabled_nb"].sum(),
                "beneficiaries_disabled_part": df["beneficiaries_disabled_nb"].sum() / (
                            df["beneficiaries_disabled_nb"] / df["beneficiaries_disabled_part"]).sum(),

                "jobs_applicants_ABC_nb_all": df["jobs_applicants_ABC_nb_all"].sum(),
                "pop_1564": df["pop_1564"].sum(),

                "jobs_applicants_ABC_nb_m25": df["jobs_applicants_ABC_nb_m25"].sum(),
                "pop_1524": df["pop_1524"].sum(),

                "neet_nb": df["neet_nb"].sum(),
                "neet_part": df["neet_nb"].sum() / (df["neet_nb"] / df["neet_part"]).sum(),

                "no_certificate_nb": df["no_certificate_nb"].sum(),
                "no_certificate_part": df["no_certificate_nb"].sum() / (
                            df["no_certificate_nb"] / df["no_certificate_part"]).sum(),
            })

        data = pd.DataFrame(result, columns=["geo_code",
                                             "nb_beneficiaries_rsa", "part_beneficiaries_rsa",
                                             "beneficiaries_disabled_nb", "pop_20p",
                                             "jobs_applicants_ABC_nb_all", "pop_1564",
                                             "jobs_applicants_ABC_nb_m25", "pop_1524",
                                             "neet_nb", "neet_part",
                                             "no_certificate_nb", "no_certificate_part"])
        data["beneficiaries_disabled_part"] = ((data["beneficiaries_disabled_nb"] / data["pop_20p"]) * 100).round(1)

        data = data.groupby(by="geo_code", as_index=False).apply(lambda df: agg_func(df))
        data = data.replace({np.nan: None})
        data = data.sort_values(by="geo_code")

        data["jobs_applicants_ABC_part_all"] = [round(ja / pop * 100, 1) if pop > 0 else 0 for ja, pop in
                                                zip(data["jobs_applicants_ABC_nb_all"], data["pop_1564"])]
        data["jobs_applicants_ABC_part_m25"] = [round(ja / pop * 100, 1) if pop > 0 else 0 for ja, pop in
                                                zip(data["jobs_applicants_ABC_nb_m25"], data["pop_1524"])]

        data.drop(columns=["pop_1564", "pop_1524"], inplace=True)
        data = data.round(1)

        return {
            "epci": data.to_dict(orient="list")
        }


class Beneficiaries(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes
        mesh = perimeter.mesh

        message_request("beneficiaries", geo_codes)
        return get_beneficiaries(geo_codes, mesh)

