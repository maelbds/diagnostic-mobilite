from compute_model.a_synthetic_population.f_database import create_table_syn_pop, create_table_syn_pop_quality
from compute_model.b_survey_association.j_database import create_table_travels, create_table_travels_analysis
from data_manager.db_functions import exists_table
from data_manager.database_connection.sql_connect import mariadb_connection_pool
from data_manager.educationdatagouv.save_data_from_csv_to_db_schools import load_schools
from data_manager.educationdatagouv.save_data_from_csv_to_db_schools_types import load_school_types
from data_manager.emp.save_data_from_csv_to_db_emp import load_emp_persons, load_emp_travels
from data_manager.emp.save_data_from_csv_to_db_modes import load_emp_modes
from data_manager.emp.save_data_from_csv_to_db_reasons import load_emp_reasons
from data_manager.esrdatagouv.save_data_from_csv_to_db_universities import load_universities
from data_manager.esrdatagouv.save_data_from_csv_to_db_universities_types import load_universities_types
from data_manager.ign.save_data_from_shp_to_db_commune_center import load_commune_center
from data_manager.ign.save_data_from_shp_to_db_commune_outline import load_commune_outline
from data_manager.ign.save_data_from_shp_to_db_commune_surface import load_commune_surface
from data_manager.ign.save_data_from_shp_to_db_epci_outline import load_epci_outline
from data_manager.insee_bpe.save_data_from_csv_to_db_bpe import load_bpe
from data_manager.insee_bpe.save_data_from_csv_to_db_bpe_types import load_bpe_types
from data_manager.insee_census.save_data_from_csv_to_db_census import load_census
from data_manager.insee_filosofi.save_data_from_csv_to_db_gridded_pop import load_gridded_pop
from data_manager.insee_general.save_data_from_csv_to_db_adjacent import load_adjacent
from data_manager.insee_general.save_data_from_csv_to_db_arrondissements import load_arrondissements
from data_manager.insee_general.save_data_from_csv_to_db_cog import load_cog_communes, load_cog_arrondissements, \
    load_cog_departements
from data_manager.insee_general.save_data_from_csv_to_db_density import load_density, load_density_types
from data_manager.insee_general.save_data_from_csv_to_db_epci import load_epci, load_epci_communes
from data_manager.insee_general.save_data_from_csv_to_db_ept import load_ept_communes, load_ept
from data_manager.insee_general.save_data_from_csv_to_db_geo import load_geo_communes
from data_manager.insee_general.save_data_from_csv_to_db_status import load_status, load_status_types
from data_manager.insee_local.save_data_from_csv_to_db_dossier_complet import load_dossier_complet
from data_manager.insee_local.save_data_from_csv_to_db_dossier_complet_status import load_dossier_complet_status
from data_manager.insee_mobpro.save_data_from_csv_to_db_mobpro2 import load_flows_mobpro
from data_manager.passage_tables.save_data_from_csv_to_db_categories import load_categories
from data_manager.passage_tables.save_data_from_csv_to_db_modes import load_modes
from data_manager.passage_tables.save_data_from_csv_to_db_modes_detailed import load_modes_detailed
from data_manager.passage_tables.save_data_from_csv_to_db_reasons import load_reasons
from data_manager.passage_tables.save_data_from_csv_to_db_types import load_types
from data_manager.transportdatagouv.clean_pt_database import delete_all_outdated_datasets
from data_manager.transportdatagouv.save_pt_to_db import create_table_agency, create_table_calendar, \
    create_table_datasets, create_table_geocodes, create_table_routes, create_table_stops, create_table_stop_times, \
    create_table_trips
from data_manager.transportdatagouv.update_pt_datasets import update_pt_datasets


def load_db():
    pool = mariadb_connection_pool()

    dbs = {
        "insee_geo_communes": load_geo_communes,

        "insee_cog_communes": load_cog_communes,
        "insee_cog_arrondissements": load_cog_arrondissements,
        "insee_cog_departements": load_cog_departements,

        "insee_epci": load_epci,
        "insee_epci_communes": load_epci_communes,
        "insee_ept": load_ept,
        "insee_ept_communes": load_ept_communes,

        "insee_arrondissements": load_arrondissements,  # arrondissements municipaux

        "insee_communes_density": load_density,
        "insee_communes_density_types": load_density_types,
        "insee_communes_status": load_status,
        "insee_communes_status_types": load_status_types,

        "osm_adjacent": load_adjacent,

        "datagouv_pt_agency": create_table_agency,
        "datagouv_pt_calendar": create_table_calendar,
        "datagouv_pt_datasets": create_table_datasets,
        "datagouv_pt_geocodes": create_table_geocodes,
        "datagouv_pt_routes": create_table_routes,
        "datagouv_pt_stops": create_table_stops,
        "datagouv_pt_stop_times": create_table_stop_times,
        "datagouv_pt_trips": create_table_trips,

        "insee_dossier_complet": load_dossier_complet,
        "insee_dossier_complet_status": load_dossier_complet_status,

        "insee_census": load_census,

        "ign_commune_center": load_commune_center,
        "ign_commune_outline": load_commune_outline,
        "ign_commune_surface": load_commune_surface,
        "ign_epci_outline": load_epci_outline,

        "insee_flows_mobpro": load_flows_mobpro,

        "insee_bpe": load_bpe,
        "insee_bpe_types": load_bpe_types,

        "educationdatagouv_schools": load_schools,
        "educationdatagouv_schools_types": load_school_types,
        "esrdatagouv_universities": load_universities,
        "esrdatagouv_universities_types": load_universities_types,

        "insee_filosofi_gridded_pop": load_gridded_pop,

        # passage tables : used with BPE and EMP
        "reasons": load_reasons,
        "categories": load_categories,
        "types": load_types,
        "modes": load_modes,
        "modes_detailed": load_modes_detailed,

        "emp_modes": load_emp_modes,
        "emp_reasons": load_emp_reasons,
        "emp_persons": load_emp_persons,
        "emp_travels": load_emp_travels,

        # to store computed data
        "computed_syn_pop": create_table_syn_pop,
        "computed_syn_pop_quality": create_table_syn_pop_quality,
        "computed_travels": create_table_travels,
        "computed_travels_analysis": create_table_travels_analysis,

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

