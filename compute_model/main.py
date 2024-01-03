import time
import pandas as pd
import os

from compute_model.b_survey_association.e_emp import get_emp_persons, get_emp_travels
from compute_model.b_survey_association.j_database import get_saved_travels_siren, save_travels, save_travels_analysis
from compute_model.b_survey_association.survey_association import compute_travels_demand
from compute_model.v_database_connection.db_request import db_request
from compute_model.a_synthetic_population.f_database import get_saved_geo_codes, \
    save_synthetic_population, save_synthetic_population_quality
from compute_model.a_synthetic_population.synthetic_population import compute_synthetic_population


def compute_and_save_synthetic_population(geo_codes):
    a = time.time()
    saved_geo_codes = get_saved_geo_codes()

    missing_geo_codes = [g for g in geo_codes if g not in saved_geo_codes]
    n_missing_geo_codes = len(missing_geo_codes)
    print(f"{len(missing_geo_codes)} missing geo_codes")

    i = 1
    for geo_code in missing_geo_codes:
        print(f"{geo_code} - {round(i/n_missing_geo_codes * 100)}%")
        census_weighted, quality = compute_synthetic_population(geo_code)
        save_synthetic_population(geo_code, census_weighted)
        save_synthetic_population_quality(geo_code, quality)
        i += 1

    b = time.time()
    print(f"{len(missing_geo_codes)} syn pop communes computed in {round(b-a)} seconds")
    return


def compute_and_save_travels(territories):
    sirens = territories["siren"].dropna().drop_duplicates().to_list()
    a = time.time()
    saved_sirens = get_saved_travels_siren()

    missing_sirens = [g for g in sirens if g not in saved_sirens]
    n_missing_sirens = len(missing_sirens)
    print(f"{len(missing_sirens)} missing siren")

    emp_persons = get_emp_persons()
    emp_travels = get_emp_travels()

    i = 1
    for siren in missing_sirens:
        print(f"{siren} - {round(i/n_missing_sirens * 100)}%")
        geo_codes = territories.loc[territories["siren"] == siren, "geo_code"].to_list()
        travels, analysis = compute_travels_demand(geo_codes, emp_persons, emp_travels)
        save_travels(travels)
        save_travels_analysis(siren, analysis)
        i += 1

    b = time.time()
    print(f"{len(missing_sirens)} EPCI travels computed in {round(b-a)} seconds")


def get_territories():
    siren = pd.read_csv("liste_EPCI_20231206.csv", dtype=str, delimiter=";", usecols=["SIREN EPCI"])
    siren_codes = siren["SIREN EPCI"].dropna().drop_duplicates().tolist()

    result = db_request(
        """ SELECT CODGEO, EPCI
            FROM insee_epci_communes
            WHERE EPCI IN :epcis
        """,
        {
            "epcis": siren_codes
        }
    )
    epcis = pd.DataFrame(result, columns=["geo_code", "siren"])

    #  COG 2021 ok / découpage de la métropole de Marseille par bassins de mobilité sinon territoire trop large (2M hab)
    met_marseille = {
        "200054807_ouest_etang": ["13078", "13039", "13098", "13077", "13056", "13047", "13063", "13044", "13029", "13092"],
        "200054807_nord_ouest": ["13103", "13035", "13105", "13049", "13053", "13003", "13024", "13115", "13008", "13069", "13009", "13051", "13037", "13118"],
        "200054807_est_etang": ["13104", "13026", "13021", "13033", "13088", "13054", "13043", "13102", "13117", "13081", "13014", "13112", "13071"],
        "200054807_marseille": ["13055", "13106", "13002", "13075"],
        "200054807_aix": ["13001", "13019", "13015", "13107", "13062", "13046", "13040", "13072", "13110", "13079", "13111", "13048", "13099", "84089", "13080", "13093", "13082", "13084", "13050", "13091", "13032", "13114", "13113", "13059", "13074", "13095", "13109", "13060", "13041", "13025", "13090", "13012", "13087"],
        "200054807_sud-est": ["13030", "13085", "13023", "13028", "13022", "13005", "13070", "13042", "13086", "13007", "83120", "13016", "13101", "13020", "13073", "13031", "13013", "13119"],
    }
    met_marseille = pd.concat([pd.DataFrame({"siren": [siren]*len(codes),
                                             "geo_code": codes}) for siren, codes in met_marseille.items()])

    result = db_request(
        """ SELECT CODGEO, EPT
            FROM insee_ept_communes
            WHERE EPT IN :ept
        """,
        {
            "ept": siren_codes
        }
    )
    epts = pd.DataFrame(result, columns=["geo_code", "siren"])

    territories = pd.concat([epcis, epts, met_marseille])
    return territories


if __name__ == '__main__':
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.width', 200)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    territories = get_territories()
    geo_codes = territories["geo_code"].drop_duplicates().to_list()
    epcis = territories["siren"].drop_duplicates().to_list()
    print(territories)

    compute_and_save_synthetic_population(geo_codes)
    compute_and_save_travels(territories)





