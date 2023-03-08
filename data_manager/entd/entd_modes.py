import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.entd.source import SOURCE_ENTD


def get_entd_modes(source=SOURCE_ENTD):
    conn = mariadb_connection()
    cur = conn.cursor()
    if source == "2018":
        cur.execute("""SELECT entd_modes_2018.id_entd, modes.id, modes.name  FROM entd_modes_2018
                        LEFT JOIN modes_detailed ON entd_modes_2018.id_mode = modes_detailed.id
                        LEFT JOIN modes ON modes_detailed.id_main_mode = modes.id""")
    result = list(cur)
    modes = pd.DataFrame(result, columns=["id_entd", "id_mode", "name_mode"])
    conn.close()
    return modes


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    ENTD_MODES = get_entd_modes("2018")
    print(ENTD_MODES)
    print(ENTD_MODES.loc[ENTD_MODES["id_entd"]=="2.3", "name_mode"].iloc[0])
