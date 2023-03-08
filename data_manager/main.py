"""
Interface to gather and prepare data used by the model
"""
import pprint

from data_manager.educationdatagouv.schools import get_schools
from data_manager.esrdatagouv.source import source_universities_label, source_universities_link
from data_manager.exception import UnknownGeocodeError

from data_manager.transportdatagouv.pt import get_public_transport as get_datagouv_pt

from data_manager.insee_bpe.bpe_places import get_bpe_places, get_bpe_places_no_schools
from data_manager.esrdatagouv.universities import get_universities

from data_manager.insee_mobpro.source import source_mobpro_label, source_mobpro_link
from data_manager.insee_local.source import source_dossier_complet_label, source_dossier_complet_link, \
    source_surface_label, source_surface_link, source_topography_label, source_topography_link, source_pop_age_link, \
    source_pop_age_label
from data_manager.insee_bpe.source import source_bpe_label, source_bpe_link
from data_manager.insee_census.source import source_census_label, source_census_link
from data_manager.transportdatagouv.source import source_transportdatagouv_label, source_transportdatagouv_link, \
    source_transportdatagouv_cycle_paths_label, source_transportdatagouv_cycle_paths_link, \
    source_transportdatagouv_cycle_parkings_label, source_transportdatagouv_cycle_parkings_link, \
    source_transportdatagouv_irve_label, source_transportdatagouv_irve_link, source_transportdatagouv_bnlc_label, \
    source_transportdatagouv_bnlc_link, source_transportdatagouv_zfe_label, source_transportdatagouv_zfe_link
from data_manager.osm.source import source_osm_label, source_osm_link
from data_manager.entd.source import source_entd_label, source_entd_link
from data_manager.educationdatagouv.source import source_schools_label, source_schools_link
from data_manager.insee_filosofi.source import source_gridded_pop_label, source_gridded_pop_link, \
    source_incomes_label, source_incomes_link
from data_manager.insee_general.source import source_aav_label, source_aav_link
from data_manager.rsvero.source import source_car_fleet_label, source_car_fleet_link
from data_manager.geodip.source import source_precariousness_label, source_precariousness_link


def get_sources():
    sources = {
        "mobpro": {
            "label": source_mobpro_label,
            "link": source_mobpro_link
        },
        "dossier_complet": {
            "label": source_dossier_complet_label,
            "link": source_dossier_complet_link
        },
        "pop_age": {
            "label": source_pop_age_label,
            "link": source_pop_age_link
        },
        "surface": {
            "label": source_surface_label,
            "link": source_surface_link
        },
        "artificialisation_rate": {
            "label": source_topography_label,
            "link": source_topography_link
        },
        "education_data_gouv": {
            "label": source_schools_label,
            "link": source_schools_link
        },
        "esr_data_gouv": {
            "label": source_universities_label,
            "link": source_universities_link
        },
        "bpe": {
            "label": source_bpe_label,
            "link": source_bpe_link
        },
        "census": {
            "label": source_census_label,
            "link": source_census_link
        },
        "gridded_pop": {
            "label": source_gridded_pop_label,
            "link": source_gridded_pop_link
        },
        "incomes": {
            "label": source_incomes_label,
            "link": source_incomes_link
        },
        "precariousness": {
            "label": source_precariousness_label,
            "link": source_precariousness_link
        },
        "aav": {
            "label": source_aav_label,
            "link": source_aav_link
        },
        "transportdatagouv": {
            "label": source_transportdatagouv_label,
            "link": source_transportdatagouv_link
        },
        "transportdatagouv_cycle_paths": {
            "label": source_transportdatagouv_cycle_paths_label,
            "link": source_transportdatagouv_cycle_paths_link
        },
        "transportdatagouv_cycle_parkings": {
            "label": source_transportdatagouv_cycle_parkings_label,
            "link": source_transportdatagouv_cycle_parkings_link
        },
        "transportdatagouv_irve": {
            "label": source_transportdatagouv_irve_label,
            "link": source_transportdatagouv_irve_link
        },
        "transportdatagouv_bnlc": {
            "label": source_transportdatagouv_bnlc_label,
            "link": source_transportdatagouv_bnlc_link
        },
        "transportdatagouv_zfe": {
            "label": source_transportdatagouv_zfe_label,
            "link": source_transportdatagouv_zfe_link
        },
        "critair": {
            "label": source_car_fleet_label,
            "link": source_car_fleet_link
        },
        "osm": {
            "label": source_osm_label,
            "link": source_osm_link
        },
        "entd": {
            "label": source_entd_label,
            "link": source_entd_link
        },
        "analysis": {
            "label": "Méthodologie de traitement",
            "link": "https://mobam.fr/diagnostic-mobilite/docs/methodologie_traitement_v1.pdf"
        },
        "model": {
            "label": "Méthodologie de modélisation",
            "link": "https://mobam.fr/diagnostic-mobilite/docs/methodologie_modelisation_v1.pdf"
        }
    }
    return sources


def get_public_transport(pool, geo_codes):
    datagouv_pt = get_datagouv_pt(pool, geo_codes)
    return datagouv_pt


def get_places(pool, geo_code):
    places = get_bpe_places_no_schools(pool, geo_code) + get_schools(pool, geo_code) + get_universities(pool, geo_code)
    return places


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_sources())
    except UnknownGeocodeError as e:
        print(e.message)
