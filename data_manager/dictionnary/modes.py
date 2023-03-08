import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection

from data_manager.entd.source import SOURCE_ENTD


def get_modes_entd(pool, source_entd=SOURCE_ENTD):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    if source_entd == "2008":
        cur.execute("""
        SELECT entd_modes_2008.id_entd, entd_modes_2008.id_mode, modes.name, modes.name_fr, modes.ghg_emissions_factor, modes.cost_factor
                FROM entd_modes_2008
                JOIN modes
                ON entd_modes_2008.id_mode = modes.id""")
    elif source_entd == "2018":
        cur.execute("""
        SELECT entd_modes_2018.id_entd, entd_modes_2018.id_mode, modes.name, modes.name_fr, modes_detailed.ghg_emissions_factor, modes_detailed.cost_factor
                FROM entd_modes_2018
                JOIN modes_detailed ON entd_modes_2018.id_mode = modes_detailed.id
                JOIN modes ON modes_detailed.id_main_mode = modes.id""")
    result = list(cur)
    modes_entd = pd.DataFrame(result, columns=["id_mode_entd", "id_mode", "name", "name_fr", "ghg_emissions_factor", "cost_factor"]
                              ).set_index("id_mode_entd")
    conn.close()
    return modes_entd


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    modes = get_modes_entd(None)
    print(modes)
    print(modes.dtypes)
