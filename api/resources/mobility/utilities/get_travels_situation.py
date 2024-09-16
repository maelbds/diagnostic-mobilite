import pandas as pd

from compute_model.database_connection.db_request import db_request
from compute_model.main import get_epcis_coverage
from api.resources.common.cog import COG

epcis_coverage = get_epcis_coverage()
epcis_covered = epcis_coverage.loc[epcis_coverage["is_covered_by_emd"] == "x"]

result = db_request(
    """ SELECT CODGEO
        FROM insee_epci_communes
        WHERE EPCI IN :epcis
        AND year_cog = :year_cog
        """,
    {
        "epcis": epcis_covered["epci"].to_list(),
        "year_cog": "2021"
    })
covered_communes = pd.DataFrame(result, columns=["geo_code"], dtype=str)


def get_travels_situation(geo_codes):
    result = db_request(
        """SELECT p_res.CODGEO_DES
        
           FROM emd_perimeter AS p

           LEFT JOIN insee_arrondissements_passage AS arr_res ON p.geo_code = arr_res.geo_code_district
           LEFT JOIN insee_passage_cog AS p_res ON arr_res.geo_code_city = p_res.CODGEO_INI

           WHERE p_res.CODGEO_DES IN :geo_codes
           AND p_res.year_cog = :cog
           AND arr_res.year_cog = :cog
           
           """,
        {
            "geo_codes": geo_codes,
            "cog": COG
        })

    travels_emd = pd.DataFrame(result, columns=["geo_code"], dtype=str).drop_duplicates()

    if all([g in travels_emd["geo_code"].to_list() for g in geo_codes]):
        return "emd"

    result = db_request(
        """ SELECT  ct.geo_code
            FROM computed_travels AS ct
            WHERE ct.geo_code IN :geo_codes
            """,
        {
            "geo_codes": geo_codes
        })

    travels_model = pd.DataFrame(result, columns=["geo_code"], dtype=str).drop_duplicates()

    if all([g in travels_model["geo_code"].to_list() for g in geo_codes]):
        return "model"

    if all([g in travels_emd["geo_code"].to_list() + travels_model["geo_code"].to_list() for g in geo_codes]):
        return "emd_and_model"

    if any([g in covered_communes["geo_code"].to_list() for g in geo_codes]):
        return "emd_not_added"

    return "not_covered"


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    print("ok")

    print(get_travels_situation(["69123"]))
    print(get_travels_situation(["34315"]))
    print(get_travels_situation(["34172"]))
    print(get_travels_situation(["75056"]))
    print(get_travels_situation(["79048"]))
    print(get_travels_situation(["79"]))

