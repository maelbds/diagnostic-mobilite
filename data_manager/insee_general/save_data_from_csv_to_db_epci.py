"""
To load INSEE EPCI from csv to database | EXECUTE ONCE

https://www.insee.fr/fr/information/2510634
"""
import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection


def load_data():
    """
    Read data from csv file & add it to the database
    :return:
    """
    cols_communes = ["CODGEO", "EPCI", "LIBEPCI", "DEP", "REG"]
    cols_details = ["EPCI", "NATURE_EPCI", "NB_COM"]

    epci_communes = pd.read_csv("data/2022/epci_communes.csv", sep=";", dtype="str", usecols=cols_communes)
    epci_details = pd.read_csv("data/2022/epci_details.csv", sep=";", dtype="str", usecols=cols_details).dropna()

    print(epci_communes)
    print(epci_details)

    epci = pd.merge(epci_communes, epci_details, right_on="EPCI", left_on="EPCI")
    epci["source"] = "EPCI 2022"

    print(epci)

    return epci


def save_data_epci_communes(epci_communes):
    conn = mariadb_connection()
    cur = conn.cursor()

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_communes_epci  
                                    (geo_code, 
                                     epci_siren,
                                     source
                                     ) VALUES (?,?,?)""", cols)

    [request(cur, [geo_code,
                   epci_code,
                   source])
     for geo_code,
         epci_code,
         source
     in zip(epci_communes["CODGEO"],
            epci_communes["EPCI"],
            epci_communes["source"])]

    conn.commit()
    conn.close()


def save_data_epci(epci):
    epci = epci.drop(columns="CODGEO").drop_duplicates().drop_duplicates(subset="EPCI")
    conn = mariadb_connection()
    cur = conn.cursor()

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_epci  
                                    (epci_siren, 
                                     epci_name,
                                     epci_type,
                                     epci_commune_nb,
                                     dep_code,
                                     region_code,
                                     source) VALUES (?,?,?,?,?,?,?)""", cols)

    [request(cur, [epci_siren,
                   epci_name,
                   epci_type,
                   epci_commune_nb,
                   dep_code,
                   region_code,
                   source])
     for epci_siren,
         epci_name,
         epci_type,
         epci_commune_nb,
         dep_code,
         region_code,
         source
     in zip(epci["EPCI"],
            epci["LIBEPCI"],
            epci["NATURE_EPCI"],
            epci["NB_COM"],
            epci["DEP"],
            epci["REG"],
            epci["source"])]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    epci = load_data()
    print(epci)
    # to prevent from unuseful loading data
    security = True
    if not security:
        save_data_epci(epci)
        save_data_epci_communes(epci)
