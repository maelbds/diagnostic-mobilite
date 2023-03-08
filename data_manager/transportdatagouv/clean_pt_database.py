import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection


def get_outdated_datasets():
    conn = mariadb_connection()
    cur = conn.cursor()
    cur.execute("""SELECT datagouv_id, name, end_calendar_validity
                FROM datagouv_pt_datasets  
                WHERE end_calendar_validity < CURDATE()
                """)
    result = list(cur)
    datasets = pd.DataFrame(result, columns=["datagouv_id", "name", "end_calendar_validity"])
    conn.close()
    return datasets


def delete_dataset(datagouv_id):
    conn = mariadb_connection()
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
    return


if __name__ == '__main__':
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    outdated_datasets = get_outdated_datasets()
    print(outdated_datasets)

    #delete_dataset("fd54f81f-4389-4e73-be75-491133d011c3")