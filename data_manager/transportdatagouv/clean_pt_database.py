import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection


def get_outdated_datasets(pool):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT datagouv_id, name, end_calendar_validity
                FROM datagouv_pt_datasets  
                WHERE end_calendar_validity < CURDATE()
                """)
    result = list(cur)
    datasets = pd.DataFrame(result, columns=["datagouv_id", "name", "end_calendar_validity"])
    conn.close()
    return datasets


def delete_dataset(pool, datagouv_id):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""DELETE 
                FROM datagouv_pt_agency  
                WHERE datagouv_id = ?
                """, [datagouv_id])
    cur.execute("""DELETE 
                FROM datagouv_pt_calendar  
                WHERE datagouv_id = ?
                """, [datagouv_id])
    cur.execute("""DELETE 
                FROM datagouv_pt_datasets  
                WHERE datagouv_id = ?
                """, [datagouv_id])
    cur.execute("""DELETE 
                FROM datagouv_pt_geocodes  
                WHERE datagouv_id = ?
                """, [datagouv_id])
    cur.execute("""DELETE 
                FROM datagouv_pt_routes  
                WHERE datagouv_id = ?
                """, [datagouv_id])
    cur.execute("""DELETE 
                FROM datagouv_pt_stops  
                WHERE datagouv_id = ?
                """, [datagouv_id])
    cur.execute("""DELETE 
                FROM datagouv_pt_stop_times  
                WHERE datagouv_id = ?
                """, [datagouv_id])
    cur.execute("""DELETE 
                FROM datagouv_pt_trips  
                WHERE datagouv_id = ?
                """, [datagouv_id])

    conn.commit()
    conn.close()
    print(f"deleted : {datagouv_id}")
    return


def delete_all_outdated_datasets(pool):
    outdated_datasets = get_outdated_datasets(pool)

    for i in outdated_datasets["datagouv_id"]:
        delete_dataset(pool, i)

    print("outdated pt datasets deleted")
    return


if __name__ == '__main__':
    delete_all_outdated_datasets(None)

    outdated_datasets = get_outdated_datasets(None)
    print(outdated_datasets)
    #delete_dataset("fd54f81f-4389-4e73-be75-491133d011c3")