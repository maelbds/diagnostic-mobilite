"""
Interface to gather and prepare data used by the model
"""
import pprint

from data_manager.computed.source import source_services_dist_label, source_services_dist_link
from data_manager.data_inclusion.source import source_data_inclusion_label, source_data_inclusion_link
from data_manager.esrdatagouv.source import source_universities_label, source_universities_link
from data_manager.exception import UnknownGeocodeError
from data_manager.ign.source import source_roads_label, source_roads_link
from data_manager.observatoire_territoire.source import source_pnr_label, source_petr_label, source_petr_link, \
    source_pnr_link, source_cnaf_dser_label, source_cnaf_dser_link, source_dares_label, source_dares_link, \
    source_insee_rp_label, source_insee_rp_link, source_qpv_link, source_qpv_label, source_dg_coll_link, \
    source_dg_coll_label, source_filosofi_label, source_filosofi_link, source_cnaf_fileas_label, \
    source_cnaf_fileas_link, source_insee_drees_label, source_insee_drees_link, source_solde_mig_label, \
    source_solde_mig_link, source_evol_rate_future_label, source_evol_rate_future_link, source_zrr_label, \
    source_zrr_link, source_onisr_label, source_onisr_link
from data_manager.pole_emploi.source import source_pole_emploi_label, source_pole_emploi_link
from data_manager.sncf.source import source_railways_label, source_railways_link, source_railways_stations_label, \
    source_railways_stations_link


from data_manager.insee_mobpro.source import source_mobpro_label, source_mobpro_link, source_mobpro_distance_link, \
    source_mobpro_distance_label
from data_manager.insee_local.source import source_dossier_complet_label, source_dossier_complet_link, \
    source_surface_label, source_surface_link, source_topography_label, source_topography_link, source_pop_age_link, \
    source_pop_age_label, source_dc_mobin_label, source_dc_mobin_link
from data_manager.insee_bpe.source import source_bpe_label, source_bpe_link
from data_manager.insee_census.source import source_census_label, source_census_link
from data_manager.transportdatagouv.source import source_transportdatagouv_label, source_transportdatagouv_link, \
    source_transportdatagouv_cycle_paths_label, source_transportdatagouv_cycle_paths_link, \
    source_transportdatagouv_cycle_parkings_label, source_transportdatagouv_cycle_parkings_link, \
    source_transportdatagouv_irve_label, source_transportdatagouv_irve_link, source_transportdatagouv_bnlc_label, \
    source_transportdatagouv_bnlc_link, source_transportdatagouv_zfe_label, source_transportdatagouv_zfe_link, \
    source_covoiturage_label, source_covoiturage_link
from data_manager.osm.source import source_osm_label, source_osm_link
from data_manager.entd.source import source_entd_label, source_entd_link
from data_manager.educationdatagouv.source import source_schools_label, source_schools_link
from data_manager.insee_filosofi.source import source_gridded_pop_label, source_gridded_pop_link, \
    source_incomes_label, source_incomes_link
from data_manager.insee_general.source import source_aav_label, source_aav_link, source_cog_link, source_cog_label
from data_manager.rsvero.source import source_car_fleet_label, source_car_fleet_link
from data_manager.geodip.source import source_precariousness_label, source_precariousness_link


def get_sources():
    sources = {
        "mobpro": {
            "label": source_mobpro_label,
            "link": source_mobpro_link
        },
        "mobpro_distance": {
            "label": source_mobpro_distance_label,
            "link": source_mobpro_distance_link
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
        "transportdatagouv_rpc": {
            "label": source_covoiturage_label,
            "link": source_covoiturage_link
        },
        "critair": {
            "label": source_car_fleet_label,
            "link": source_car_fleet_link
        },
        "osm": {
            "label": source_osm_label,
            "link": source_osm_link
        },
        "sncf_railways": {
            "label": source_railways_label,
            "link": source_railways_link
        },
        "sncf_stations": {
            "label": source_railways_stations_label,
            "link": source_railways_stations_link
        },
        "ign_roads": {
            "label": source_roads_label,
            "link": source_roads_link
        },
        "entd": {
            "label": source_entd_label,
            "link": source_entd_link
        },
        "petr": {
            "label": source_petr_label,
            "link": source_petr_link
        },
        "pnr": {
            "label": source_pnr_label,
            "link": source_pnr_link
        },
        "zrr": {
            "label": source_zrr_label,
            "link": source_zrr_link
        },
        "cog": {
            "label": source_cog_label,
            "link": source_cog_link
        },
        "insee_rp": {
            "label": source_insee_rp_label,
            "link": source_insee_rp_link
        },
        "insee_dc_mobin": {
            "label": source_dc_mobin_label,
            "link": source_dc_mobin_link
        },
        "insee_solde_mig": {
            "label": source_solde_mig_label,
            "link": source_solde_mig_link
        },
        "insee_evol_rate_future": {
            "label": source_evol_rate_future_label,
            "link": source_evol_rate_future_link
        },
        "pole_emploi": {
            "label": source_pole_emploi_label,
            "link": source_pole_emploi_link
        },
        "data_inclusion": {
            "label": source_data_inclusion_label,
            "link": source_data_inclusion_link
        },
        "qpv": {
            "label": source_qpv_label,
            "link": source_qpv_link
        },
        "cnaf_dser": {
            "label": source_cnaf_dser_label,
            "link": source_cnaf_dser_link
        },
        "cnaf_fileas": {
            "label": source_cnaf_fileas_label,
            "link": source_cnaf_fileas_link
        },
        "onisr": {
            "label": source_onisr_label,
            "link": source_onisr_link
        },
        "insee_drees": {
            "label": source_insee_drees_label,
            "link": source_insee_drees_link
        },
        "dares": {
            "label": source_dares_label,
            "link": source_dares_link
        },
        "dg_coll": {
            "label": source_dg_coll_label,
            "link": source_dg_coll_link
        },
        "services_dist": {
            "label": source_services_dist_label,
            "link": source_services_dist_link
        },
        "insee_filosofi": {
            "label": source_filosofi_label,
            "link": source_filosofi_link
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


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_sources())
    except UnknownGeocodeError as e:
        print(e.message)
