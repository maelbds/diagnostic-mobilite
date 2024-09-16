from data_manager.database_connection.sql_connect import mariadb_connection_pool
from data_manager.transportdatagouv.clean_pt_database import delete_all_outdated_datasets
from data_manager.transportdatagouv.save_bnlc_to_db import load_bnlc
from data_manager.transportdatagouv.save_cycle_parkings_to_db import load_cycle_parkings
from data_manager.transportdatagouv.save_cycle_paths_to_db import load_cycle_paths
from data_manager.transportdatagouv.save_irve_to_db import load_irve
from data_manager.transportdatagouv.update_pt_datasets import update_pt_datasets


def update_db():
    pool = mariadb_connection_pool()

    print("--- updating irve...")
    load_irve(pool, "transportdatagouv_irve")

    print("--- updating bnlc...")
    load_bnlc(pool, "transportdatagouv_bnlc")

    print("--- updating cycle parkings...")
    load_cycle_parkings(pool, "transportdatagouv_cycle_parkings")

    print("--- updating cycle paths...")
    load_cycle_paths(pool, "transportdatagouv_cycle_paths")

    print("--- updating public transport...")
    delete_all_outdated_datasets(pool)
    update_pt_datasets(pool)


if __name__ == '__main__':
    update_db()

