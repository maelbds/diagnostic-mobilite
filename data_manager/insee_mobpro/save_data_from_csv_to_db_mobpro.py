"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import csv
import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection


def read_raw_csv():
    census = pd.read_csv("data/2018/FD_MOBPRO_2018.csv", sep=";", dtype="str")
    print(census)


def create_light_csv():
    useful_cols = ["COMMUNE", "ARM", "DCFLT", "DCLT", "CS1", "EMPL", "ILTUU", "ILT", "IPONDI", "METRODOM", "NA5",
                   "STAT", "TP", "TRANS", "TYPMR", "VOIT"]
    census = pd.read_csv("data/2018/FD_MOBPRO_2018.csv", sep=";", dtype="str", usecols=useful_cols)
    print(census)
    census.to_csv("data/2018/FD_MOBPRO_2018_light.csv")


def create_super_light_csv():
    useful_cols = ["COMMUNE", "ARM", "DCFLT", "DCLT", "IPONDI", "METRODOM"]
    census = pd.read_csv("data/2018/FD_MOBPRO_2018.csv", sep=";", dtype="str", usecols=useful_cols)
    print(census)
    census.to_csv("data/2018/FD_MOBPRO_2018_super_light.csv")


def get_flows_from_csv():
    useful_cols = ["COMMUNE", "ARM", "DCFLT", "DCLT", "IPONDI", "TRANS", "TP"]
    mobpro = pd.read_csv("data/2018/FD_MOBPRO_2018_light.csv", sep=",", dtype="str", usecols=useful_cols)
    mobpro = mobpro.astype({"IPONDI": "float64"})

    print(mobpro.groupby(by=["TRANS"]).apply(lambda df: df.groupby("TP").sum()/df["IPONDI"].sum()))
    print(mobpro[mobpro["COMMUNE"] == "38509"].groupby(by=["TRANS"]).apply(lambda df: df.groupby("TP").sum()/df["IPONDI"].sum()))

    print(mobpro.groupby(by=["TP"]).sum())
    print((mobpro.groupby(by=["TP"]).sum()/mobpro["IPONDI"].sum()*100).round(1))

    print(mobpro.groupby(by=["TRANS"]).sum())
    print((mobpro.groupby(by=["TRANS"]).sum()/mobpro["IPONDI"].sum()*100).round(1))

    # To merge foreign communes
    dcflt_mask = mobpro["DCLT"] == "99999"
    mobpro.loc[dcflt_mask, "DCLT"] = mobpro.loc[dcflt_mask, "DCFLT"]
    print(mobpro)

    flows = mobpro.groupby(by=["COMMUNE", "DCLT", "TRANS"]).sum()
    print(flows)
    print(flows.sum())

    flows = flows.reset_index()
    return flows


def save_data_to_db(flows):
    conn = mariadb_connection()
    cur = conn.cursor()

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_flows_home_work 
                            (geo_code_home, 
                             geo_code_work, 
                             TRANS, 
                             flow,
                             date,
                             source) VALUES (?,?,?,?,CURRENT_TIMESTAMP, ?)""", cols)

    [request(cur, [geo_code_home, geo_code_work, trans, flow, "MOBPRO_2018"])
     for geo_code_home, geo_code_work, trans, flow
     in zip(flows["COMMUNE"], flows["DCLT"], flows["TRANS"], flows["IPONDI"])]

    conn.commit()
    conn.close()



# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 1500)

    flows = get_flows_from_csv()
    print(flows)
    # to prevent from unuseful loading data
    security = True
    if not security:
        save_data_to_db(flows)
