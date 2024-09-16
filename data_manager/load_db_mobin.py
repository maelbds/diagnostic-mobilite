from data_manager.computed.services_dist import load_services_dist
from data_manager.data_inclusion.save_data_inclusion import load_datainclusion
from data_manager.db_functions import exists_table
from data_manager.database_connection.sql_connect import mariadb_connection_pool
from data_manager.educationdatagouv.save_data_from_csv_to_db_schools_types import load_school_types
from data_manager.educationdatagouv.save_data_from_csv_to_db_schools import load_schools
from data_manager.ign.save_data_from_shp_to_db_commune_center import load_commune_center
from data_manager.ign.save_data_from_shp_to_db_commune_outline import load_commune_outline
from data_manager.ign.save_data_from_shp_to_db_epci_outline import load_epci_outline
from data_manager.ign.save_data_from_shp_to_db_routes import load_routes, load_routes_communes
from data_manager.insee_bpe.save_data_from_csv_to_db_bpe import load_bpe
from data_manager.insee_bpe.save_data_from_csv_to_db_bpe_types import load_bpe_types
from data_manager.insee_filosofi.save_data_from_csv_to_db_gridded_pop import load_gridded_pop
from data_manager.insee_general.save_data_from_csv_to_db_aav import load_aav, load_aav_communes, load_aav_communes_cat, \
    load_aav_types
from data_manager.insee_general.save_data_from_csv_to_db_adjacent import load_adjacent
from data_manager.insee_general.save_data_from_csv_to_db_arrondissements import load_arrondissements
from data_manager.insee_general.save_data_from_csv_to_db_code_postal import load_code_postal
from data_manager.insee_general.save_data_from_csv_to_db_cog import load_cog_communes, load_cog_arrondissements, \
    load_cog_departements
from data_manager.insee_general.save_data_from_csv_to_db_cog_evenement import load_cog_evenements
from data_manager.insee_general.save_data_from_csv_to_db_density import load_density, load_density_types
from data_manager.insee_general.save_data_from_csv_to_db_epci import load_epci, load_epci_communes
from data_manager.insee_general.save_data_from_csv_to_db_status import load_status, load_status_types
from data_manager.insee_local.save_data_from_csv_to_db_dossier_complet_mobin import load_dossier_complet_mobin
from data_manager.insee_mobpro.save_data_from_csv_to_db_mobpro2 import load_flows_mobpro
from data_manager.insee_mobpro.save_data_from_csv_to_db_mobpro_distance_co2 import load_flows_mobpro_distance
from data_manager.observatoire_territoire.save_data_from_csv_to_db_cnaf_apa import load_cnaf_apa
from data_manager.observatoire_territoire.save_data_from_csv_to_db_cnaf_dser_rsa import load_cnaf_dser_rsa
from data_manager.observatoire_territoire.save_data_from_csv_to_db_dares_demandeurs_emploi import load_dares
from data_manager.observatoire_territoire.save_data_from_csv_to_db_dg_collectivites_perequation import \
    load_perequation_epci, load_perequation_communes
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_drees_min_vieillesse import load_drees
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_filosofi_pauvrete import \
    load_filosofi_pauvrete_com, load_filosofi_pauvrete_epci
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_rp_2016_solde_mirgatoire_csp import \
    load_solde_mig
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_rp_anct_qpv import load_qpv
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_rp_arrivants import load_arrivants
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_rp_emploi import load_emploi
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_rp_emploi_partiel import load_emploi_partiel
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_rp_emploi_partiel_epci import \
    load_emploi_partiel_epci
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_rp_emploi_precaire import load_emploi_precaire
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_rp_emploi_precaire_epci import \
    load_emploi_precaire_epci
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_rp_etrangers_immigres import \
    load_etrangers_immigres
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_rp_menages import load_menages
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_rp_neet import load_neet
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_rp_pop import load_rp_pop, load_rp_pop_epci
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_rp_pop_evolution_dep import \
    load_pop_evol_passe, load_pop_evol_futur
from data_manager.observatoire_territoire.save_data_from_csv_to_db_insee_rp_taux_emploi_epci import \
    load_taux_emploi_epci
from data_manager.observatoire_territoire.save_data_from_csv_to_db_onisr_securite_routiere import load_securite_routiere
from data_manager.observatoire_territoire.save_data_from_csv_to_db_perimeters import load_petr, load_pnr, load_zrr
from data_manager.pole_emploi.save_data_pole_emploi import load_pole_emploi_agencies, load_pole_emploi_agencies_zones
from data_manager.rsvero.save_data_from_xls_to_db_car_fleet import load_car_fleet
from data_manager.sncf.save_data_from_csv_to_db_railway_stations import load_railway_stations
from data_manager.sncf.save_data_from_shp_to_db_railways import load_railways, load_railways_communes
from data_manager.transportdatagouv.clean_pt_database import delete_all_outdated_datasets
from data_manager.transportdatagouv.save_bnlc_to_db import load_bnlc
from data_manager.transportdatagouv.save_cycle_parkings_to_db import load_cycle_parkings
from data_manager.transportdatagouv.save_cycle_paths_to_db import load_cycle_paths
from data_manager.transportdatagouv.save_irve_to_db import load_irve
from data_manager.transportdatagouv.save_pt_to_db import create_table_agency, create_table_calendar, \
    create_table_datasets, create_table_geocodes, create_table_routes, create_table_stops, create_table_stop_times, \
    create_table_trips
from data_manager.transportdatagouv.save_rpc_to_db import load_rpc
from data_manager.transportdatagouv.update_pt_datasets import update_pt_datasets


def load_db():
    pool = mariadb_connection_pool()

    dbs = {
        "educationdatagouv_schools": load_schools,
        "educationdatagouv_schools_types": load_school_types,

        "ign_commune_center": load_commune_center,
        "ign_commune_outline": load_commune_outline,
        "ign_epci_outline": load_epci_outline,

        "insee_bpe": load_bpe,
        "insee_bpe_types": load_bpe_types,

        "insee_aav": load_aav,
        "insee_aav_communes": load_aav_communes,
        "insee_aav_communes_cat": load_aav_communes_cat,
        "insee_aav_types": load_aav_types,

        "osm_adjacent": load_adjacent,
        "la_poste_code_postal": load_code_postal,
        "insee_cog_evenements": load_cog_evenements,
        "insee_communes_density": load_density,
        "insee_communes_density_types": load_density_types,
        "insee_epci": load_epci,
        "insee_epci_communes": load_epci_communes,
        "insee_communes_status": load_status,
        "insee_communes_status_types": load_status_types,
        "insee_arrondissements": load_arrondissements,

        "insee_cog_communes": load_cog_communes,
        "insee_cog_arrondissements": load_cog_arrondissements,
        "insee_cog_departements": load_cog_departements,

        "observatoire_cnaf_fileas_apa": load_cnaf_apa,
        "observatoire_cnaf_dser_rsa_disabled": load_cnaf_dser_rsa,
        "observatoire_dares_demandeurs_emploi": load_dares,
        "observatoire_dg_collectivites_budget_com": load_perequation_communes,
        "observatoire_dg_collectivites_budget_epci": load_perequation_epci,
        "observatoire_insee_drees_old_age": load_drees,
        "observatoire_insee_filosofi_pauvrete_com": load_filosofi_pauvrete_com,
        "observatoire_insee_filosofi_pauvrete_epci": load_filosofi_pauvrete_epci,
        "observatoire_insee_rp_solde_migratoire_csp_dep": load_solde_mig,
        "observatoire_insee_rp_anct_qpv": load_qpv,
        "observatoire_insee_rp_arrivants": load_arrivants,
        "observatoire_insee_rp_emploi": load_emploi,
        "observatoire_insee_rp_taux_emploi_epci": load_taux_emploi_epci,
        "observatoire_insee_rp_emploi_partiel": load_emploi_partiel,
        "observatoire_insee_rp_emploi_partiel_epci": load_emploi_partiel_epci,
        "observatoire_insee_rp_emploi_precaire": load_emploi_precaire,
        "observatoire_insee_rp_emploi_precaire_epci": load_emploi_precaire_epci,
        "observatoire_insee_rp_etrangers_immigres": load_etrangers_immigres,
        "observatoire_insee_rp_menages": load_menages,
        "observatoire_insee_rp_neet_certificate": load_neet,
        "observatoire_insee_rp_pop": load_rp_pop,
        "observatoire_insee_rp_pop_epci": load_rp_pop_epci,
        "observatoire_insee_rp_pop_evolution_passe_dep": load_pop_evol_passe,
        "observatoire_insee_rp_pop_evolution_futur_dep": load_pop_evol_futur,
        "observatoire_onisr_securite_routiere_dep": load_securite_routiere,
        "observatoire_petr": load_petr,
        "observatoire_pnr": load_pnr,
        "observatoire_zrr": load_zrr,

        "pole_emploi_agencies": load_pole_emploi_agencies,
        "pole_emploi_agencies_zones": load_pole_emploi_agencies_zones,

        "insee_flows_mobpro": load_flows_mobpro,
        "insee_flows_mobpro_distance": load_flows_mobpro_distance,

        "insee_filosofi_gridded_pop": load_gridded_pop,

        "rsvero_critair": load_car_fleet,

        "transportdatagouv_bnlc": load_bnlc,
        "transportdatagouv_cycle_parkings": load_cycle_parkings,
        "transportdatagouv_cycle_paths": load_cycle_paths,
        "transportdatagouv_irve": load_irve,

        "sncf_railways": load_railways,
        "sncf_railways_communes": load_railways_communes,
        "sncf_stations": load_railway_stations,

        "ign_routes": load_routes,
        "ign_routes_communes": load_routes_communes,

        "insee_dossier_complet_mobin": load_dossier_complet_mobin,

        "datagouv_pt_agency": create_table_agency,
        "datagouv_pt_calendar": create_table_calendar,
        "datagouv_pt_datasets": create_table_datasets,
        "datagouv_pt_geocodes": create_table_geocodes,
        "datagouv_pt_routes": create_table_routes,
        "datagouv_pt_stops": create_table_stops,
        "datagouv_pt_stop_times": create_table_stop_times,
        "datagouv_pt_trips": create_table_trips,

        "datainclusion": load_datainclusion,

        "transportdatagouv_rpc": load_rpc,

        "terristory_services_dist": load_services_dist,
    }

    print("loading databases")
    for name_table, func in dbs.items():
        if not exists_table(pool, name_table):
            func(pool, name_table)
        else:
            print(f"{name_table} - already saved...")
    
    print("updating pt database")
    delete_all_outdated_datasets(pool)
    update_pt_datasets(pool)


if __name__ == '__main__':
    load_db()

