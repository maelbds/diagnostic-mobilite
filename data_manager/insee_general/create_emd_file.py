import pandas as pd
import json
import os

from api.resources.common.db_request import db_request
from compute_model.main import get_epcis_coverage

folder = "selection_map_files"


def create_emd(year_cog):
    result = db_request(
        """SELECT p_res.CODGEO_DES

           FROM emd_perimeter AS p

           LEFT JOIN insee_arrondissements_passage AS arr_res ON p.geo_code = arr_res.geo_code_district
           LEFT JOIN insee_passage_cog AS p_res ON arr_res.geo_code_city = p_res.CODGEO_INI

           WHERE p_res.year_cog = :cog
           AND p.emd_id = "montpellier"
           AND arr_res.year_cog = :cog
           """,
        {
            "cog": year_cog
        })

    emd_added = pd.DataFrame(result, columns=["geo_code"], dtype=str)["geo_code"].drop_duplicates().to_list()

    epcis_coverage = get_epcis_coverage()
    mask_epci_not_added = (epcis_coverage["is_covered_by_emd"] == "x") & (epcis_coverage["is_emd_added"] != "x")
    epcis_not_added = epcis_coverage.loc[mask_epci_not_added, "epci"].to_list()

    result = db_request(
        """SELECT e.CODGEO

           FROM insee_epci_communes AS e

           WHERE e.EPCI IN :epcis
           AND e.year_cog = :cog
           """,
        {
            "epcis": epcis_not_added,
            "cog": year_cog
        })

    emd_not_added = pd.DataFrame(result, columns=["geo_code"], dtype=str).drop_duplicates()["geo_code"].to_list()

    emd = {
        "emd_added": emd_added,
        "emd_not_added": emd_not_added,
    }

    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    with open(f"{folder}/{year_cog}/emd.json", 'w') as f:
        json.dump(emd, f)


if __name__ == '__main__':
    year_cog = 2023
    create_emd(year_cog)

