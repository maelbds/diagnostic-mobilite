"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import csv
import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection


def read_gridded_pop_csv():
    useful_cols = ["Idcar_200m", "lcog_geo", "Ind", "Men", "Men_pauv", "Men_prop", "Ind_snv", "Men_surf"]
    g_pop = pd.read_csv("data/2017/Filosofi2017_carreaux_200m_csv/Filosofi2017_carreaux_200m_met.csv", sep=",",
                        dtype="str", usecols=useful_cols)
    g_pop = g_pop.rename(columns={"Idcar_200m": "idGrid200", "lcog_geo": "geo_code"})
    g_pop = g_pop.astype({"Ind": "float", "Men": "float",
                          "Men_pauv": "float", "Men_prop": "float",
                          "Ind_snv": "float", "Men_surf": "float"})
    g_pop["geo_code"] = g_pop["geo_code"].apply(lambda x: x[:5])
    print(g_pop)
    print(g_pop.sort_values(by="geo_code", ascending=False))
    lc = g_pop[g_pop["geo_code"] == "79048"]
    print(lc["Ind"].sum())
    print(lc["Men"].sum())
    print(lc["Men_pauv"].sum())
    print(lc["Men_prop"].sum())
    print(lc["Ind_snv"].sum())
    print(lc["Men_surf"].sum())
    return g_pop


def save_data_to_db(gridded_pop):
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in gridded_pop.columns]) + ", source)"
    values_name = "(" + ", ".join(["?" for col in gridded_pop.columns]) + ", 'FILOSOFI_2017')"

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_filosofi_gridded_pop """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in gridded_pop.iterrows()]

    conn.commit()
    conn.close()
    print("done")
    return


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    g_pop = read_gridded_pop_csv()
    # to prevent from unuseful loading data
    security = True
    if not security:
        save_data_to_db(g_pop)
