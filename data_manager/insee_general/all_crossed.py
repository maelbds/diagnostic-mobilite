import pandas as pd
from shapely import wkb
import json

from data_manager.database_connection.sql_connect import mariadb_connection

from data_manager.insee_general.source import SOURCE_EPCI, SOURCE_AAV


def get_communes_aav_epci(source_epci=SOURCE_EPCI, source_aav=SOURCE_AAV):
    conn = mariadb_connection()
    cur = conn.cursor()
    cur.execute("""SELECT insee_communes.geo_code, epci_siren, code_aav, cat_commune_aav, insee_aav.type_code
                FROM insee_communes
                JOIN insee_communes_aav ON insee_communes.geo_code = insee_communes_aav.geo_code
                JOIN insee_aav ON insee_aav.code = insee_communes_aav.code_aav
                JOIN insee_communes_epci ON insee_communes.geo_code = insee_communes_epci.geo_code
                WHERE insee_communes_epci.source = ? AND insee_communes_aav.source = ?
                """, [source_epci, source_aav])
    result = list(cur)

    conn.close()
    communes = pd.DataFrame(result, columns=["geo_code", "code_epci", "code_aav", "cat_commune_aav", "cat_aav"])

    def get_typo_aav(row):
        return row["cat_commune_aav"][0] + row["cat_aav"]
    communes["typo_aav"] = communes.apply(lambda row: get_typo_aav(row), axis=1)
    communes = communes.drop(columns=["cat_aav"])
    communes = communes.set_index("geo_code")
    return communes


def get_epci(source_epci=SOURCE_EPCI):
    conn = mariadb_connection()
    cur = conn.cursor()
    cur.execute("""SELECT epci_siren, epci_name
                FROM insee_epci
                WHERE source = ? 
                """, [source_epci])
    result = list(cur)
    epci = pd.DataFrame(result, columns=["epci_siren", "epci_name"])
    conn.close()

    epci = epci.set_index("epci_siren")
    return epci


def get_aav(source_epci=SOURCE_AAV):
    conn = mariadb_connection()
    cur = conn.cursor()
    cur.execute("""SELECT code, name
                FROM insee_aav
                WHERE source = ? 
                """, [source_epci])
    result = list(cur)
    aav = pd.DataFrame(result, columns=["code", "name"])
    conn.close()

    aav = aav.set_index("code")
    return aav

if __name__ == '__main__':
    communes = get_communes_aav_epci()
    epci = get_epci()
    aav = get_communes_aav_epci()
    print(aav)
    print(epci.to_dict()["epci_name"])


    with open('communes.json', 'w') as fp:
        json.dump(aav.to_dict(), fp)

