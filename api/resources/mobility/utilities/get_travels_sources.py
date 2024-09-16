import pandas as pd

from api.resources.mobility.utilities.get_travels_situation import get_travels_situation
from compute_model.years import year_dossier_complet, year_census, year_bpe, year_mobpro
from data_manager.sources.sources import get_label_link_for_source_year
from api.resources.common.cog import COG

from compute_model.database_connection.db_request import db_request


sources_emp_names = [
    {
        "name": "emp_persons",
        "year": "2019"
    },
    {
        "name": "insee_dossier_complet",
        "year": year_dossier_complet
    },
    {
        "name": "insee_mobpro_flows",
        "year": year_mobpro
    },
    {
        "name": "insee_bpe",
        "year": year_bpe
    },
]

sources_emp = [get_label_link_for_source_year(s["name"], s["year"]) for s in sources_emp_names]

emp_methodo = [
    {
        "label": "Méthodologie de modélisation",
        "link": "https:diagnostic-mobilite.fr/docs/methodologie_modelisation_v1.pdf"
    },
    {
        "label": "Méthodologie de traitement",
        "link": "https:diagnostic-mobilite.fr/docs/methodologie_traitement_v1.pdf"
    },
]

emd_methodo = [
    {
        "label": "Méthodologie de traitement",
        "link": "https:diagnostic-mobilite.fr/docs/methodologie_traitement_v1.pdf"
    },
]


def get_travels_sources(geo_codes):
    travels_situation = get_travels_situation(geo_codes)

    sources = []

    if travels_situation == "model":
        sources = sources_emp + emp_methodo

    elif travels_situation == "emd":
        result = db_request(
            """SELECT d.emd_name, d.emd_link
            
               FROM emd_perimeter AS p
               JOIN emd_datasets AS d ON p.emd_id = d.emd_id

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
        sources_emd = pd.DataFrame(result, columns=["label", "link"]).drop_duplicates().to_dict(orient="records")

        sources = sources_emd + emd_methodo

    return sources


if __name__ == '__main__':
    print(get_travels_sources(["69123"]))
    print(get_travels_sources(["75056"]))
    print(get_travels_sources(["79048"]))
    print(get_travels_sources(["34172"]))
    print(get_travels_sources(["34315"]))
