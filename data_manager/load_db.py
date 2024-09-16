from api.resources.common.compute_legend_intervals import save_legend_intervals
from compute_model.a_synthetic_population.f_database import create_table_syn_pop, create_table_syn_pop_quality
from compute_model.b_survey_association.j_database import create_table_travels, create_table_travels_analysis, \
    create_table_persons
from data_manager.database_connection.sql_connect import mariadb_connection_pool
from data_manager.educationdatagouv.save_data_from_csv_to_db_schools_types import load_schools_types
from data_manager.educationdatagouv.save_data_from_csv_to_db_schools import load_schools
from data_manager.emd.load_emd import load_emd
from data_manager.emp.save_data_from_csv_to_db_emp import load_emp_persons, load_emp_travels
from data_manager.emp.save_data_from_csv_to_db_modes import load_emp_modes
from data_manager.emp.save_data_from_csv_to_db_reasons import load_emp_reasons
from data_manager.esrdatagouv.save_data_from_csv_to_db_universities import load_universities
from data_manager.esrdatagouv.save_data_from_csv_to_db_universities_types import load_universities_types
from data_manager.geodip.save_data_from_csv_to_db_geodip import load_geodip
from data_manager.ign.save_data_from_shp_to_db_commune_center import load_commune_center
from data_manager.ign.save_data_from_shp_to_db_commune_outline import load_commune_outline
from data_manager.ign.save_data_from_shp_to_db_epci_outline import load_epci_outline
from data_manager.insee_bpe.save_data_from_csv_to_db_bpe import load_bpe
from data_manager.insee_bpe.save_data_from_csv_to_db_bpe_types import load_bpe_types
from data_manager.insee_census.save_data_from_csv_to_db_census import load_census
from data_manager.insee_filosofi.save_data_from_csv_to_db_filosofi import load_filosofi
from data_manager.insee_filosofi.save_data_from_csv_to_db_gridded_pop import load_gridded_pop
from data_manager.insee_general.save_data_from_csv_to_db_aav import load_aav
from data_manager.insee_general.save_data_from_csv_to_db_aav_communes import load_aav_communes
from data_manager.insee_general.save_data_from_csv_to_db_aav_dict import load_aav_communes_cat, load_aav_types
from data_manager.insee_general.save_data_from_csv_to_db_adjacent import load_adjacent
from data_manager.insee_general.save_data_from_csv_to_db_arrondissements import load_arrondissements
from data_manager.insee_general.save_data_from_csv_to_db_arrondissements_passage import load_arrondissements_passage

from data_manager.insee_general.save_data_from_csv_to_db_cog_communes import load_cog_communes
from data_manager.insee_general.save_data_from_csv_to_db_cog_arrondissements import load_cog_arrondissements
from data_manager.insee_general.save_data_from_csv_to_db_cog_departements import load_cog_departements
from data_manager.insee_general.save_data_from_csv_to_db_density import load_density, load_density_types

from data_manager.insee_general.save_data_from_csv_to_db_epci import load_epci
from data_manager.insee_general.save_data_from_csv_to_db_epci_communes import load_epci_communes
from data_manager.insee_general.save_data_from_csv_to_db_geo import load_geo_communes
from data_manager.insee_general.save_data_from_csv_to_db_passage_cog import load_passage_cog
from data_manager.insee_general.save_data_from_csv_to_db_status import load_status, load_status_types
from data_manager.insee_local.save_data_from_csv_to_db_dossier_complet import load_dossier_complet
from data_manager.insee_local.save_data_from_csv_to_db_dossier_complet_status import load_dossier_complet_status
from data_manager.insee_mobpro.save_data_from_csv_to_db_mobpro2 import load_mobpro_flows
from data_manager.insee_mobpro.save_data_from_csv_to_db_mobpro_light import load_mobpro_flows_light
from data_manager.passage_tables.save_data_from_csv_to_db_categories import load_categories
from data_manager.passage_tables.save_data_from_csv_to_db_modes import load_modes
from data_manager.passage_tables.save_data_from_csv_to_db_modes_detailed import load_modes_detailed
from data_manager.passage_tables.save_data_from_csv_to_db_reasons import load_reasons
from data_manager.passage_tables.save_data_from_csv_to_db_types import load_types

from data_manager.rsvero.save_data_from_xls_to_db_car_fleet import load_critair
from data_manager.sncf.save_data_from_csv_to_db_railway_stations import load_railway_stations
from data_manager.sncf.save_data_from_shp_to_db_railways import load_railways, load_railways_communes
from data_manager.sources.sources import create_table_sources
from data_manager.stats.create_table_stats import create_table_stats_api
from data_manager.transportdatagouv.clean_pt_database import delete_all_outdated_datasets
from data_manager.transportdatagouv.save_bnlc_to_db import load_bnlc
from data_manager.transportdatagouv.save_cycle_parkings_to_db import load_cycle_parkings
from data_manager.transportdatagouv.save_cycle_paths_to_db import load_cycle_paths
from data_manager.transportdatagouv.save_irve_to_db import load_irve
from data_manager.transportdatagouv.save_pt_to_db import create_table_datasets, create_table_agency, \
    create_table_calendar, create_table_stops, create_table_trips, create_table_stop_times, \
    create_table_geocodes, create_table_routes

from data_manager.transportdatagouv.save_zfe_to_db import load_zfe
from data_manager.transportdatagouv.update_pt_datasets import update_pt_datasets


def load_db():
    pool = mariadb_connection_pool()

    dbs_to_load = [
        create_table_sources,

        load_passage_cog,

        load_cog_communes,
        load_cog_arrondissements,
        load_cog_departements,

        load_geo_communes,

        load_aav,
        load_aav_communes,
        load_aav_types,
        load_aav_communes_cat,

        load_arrondissements,
        load_arrondissements_passage,

        load_epci,
        load_epci_communes,

        load_density,
        load_density_types,
        load_status,
        load_status_types,

        load_dossier_complet,
        load_dossier_complet_status,

        load_commune_outline,
        load_commune_center,
        load_epci_outline,

        load_adjacent,

        load_gridded_pop,
        load_filosofi,

        load_census,

        load_geodip,

        load_mobpro_flows,
        load_mobpro_flows_light,

        # passage tables : used with BPE and EMP
        load_types,
        load_categories,
        load_reasons,
        load_modes,
        load_modes_detailed,

        load_bpe,
        load_bpe_types,
        load_schools,
        load_schools_types,
        load_universities,
        load_universities_types,

        load_critair,
        load_zfe,

        load_railway_stations,
        load_railways,
        load_railways_communes,

        load_cycle_paths,
        load_cycle_parkings,

        load_bnlc,
        load_irve,

        create_table_stats_api,

        create_table_datasets,
        create_table_agency,
        create_table_calendar,
        create_table_geocodes,
        create_table_routes,
        create_table_stops,
        create_table_stop_times,
        create_table_trips,

        create_table_syn_pop,
        create_table_syn_pop_quality,
        create_table_persons,
        create_table_travels,
        create_table_travels_analysis,

        load_emp_reasons,
        load_emp_modes,
        load_emp_persons,
        load_emp_travels,

        load_emd,
    ]

    for load_func in dbs_to_load:
        load_func(pool)

    save_legend_intervals()

    print("updating pt database")
    delete_all_outdated_datasets(pool)
    update_pt_datasets(pool)


if __name__ == '__main__':
    load_db()

