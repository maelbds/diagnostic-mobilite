import requests
import pandas as pd
import numpy as np
import time

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.db_functions import load_database


def get_pole_emploi_token():
    r = requests.post("https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=/partenaire",
                     headers={
                         "Content-Type": "application/x-www-form-urlencoded"
                     },
                     data={
                         "grant_type": "client_credentials",
                         "client_id": "PAR_diagnosticmobilitesol_fd2fc858dca59422d2e54b3d2134f9ccd202af59fc5580bf2c0dc686838b294e",
                         "client_secret": "815a514c6f89bd1bf9fb95ecb8518c5ee71fad040a8ae23aaf851e92f8b231a4",
                         "scope": "api_referentielagencesv1 api_stats-perspectives-retour-emploiv1 retouremploi organisationpe"
                     })
    data = r.json()
    return data


def get_pole_emploi_agencies(token, dep):
    r = requests.get("https://api.pole-emploi.io/partenaire/referentielagences/v1/agences?zonecompetence=true&commune="+dep,
                     headers={
                         "Content-Type": "application/json",
                         "Accept": "application/json",
                         "Authorization": "Bearer " + token
                     }, )
    print("---- dep " + dep)
    print(r)
    datasets = r.json()
    agencies = pd.DataFrame(datasets, columns=["code", "libelle", "libelleEtendu", "type", "typeAccueil",
                                               "contact", "adressePrincipale", "zoneCompetences"])
    agencies["lat"] = [a["gpsLat"] for a in agencies["adressePrincipale"]]
    agencies["lon"] = [a["gpsLon"] for a in agencies["adressePrincipale"]]
    agencies["email"] = [a["email"] for a in agencies["contact"]]
    agencies["communeImplantation"] = [a["communeImplantation"] for a in agencies["adressePrincipale"]]
    agencies["zoneCompetences"] = [[c["communeInsee"] for c in a] if isinstance(a, list) else [] for a in agencies["zoneCompetences"]]
    agencies = agencies.drop(columns=["adressePrincipale", "contact"])
    print(agencies)
    return agencies


def get_couples_from_agencies(agencies):
    couples = pd.concat([pd.DataFrame({"code": [c for g in geocodes], "zoneCompetences": geocodes}) for c, geocodes in
                         zip(agencies["code"], agencies["zoneCompetences"])])
    couples = couples.drop_duplicates()
    return couples


def get_dep_from_region(reg):
    conn = mariadb_connection(None)
    cur = conn.cursor()
    cur.execute("""SELECT DEP
                FROM insee_cog_departements
                WHERE REG = ?
                AND year_data = ?
                """, [reg, "2022"])
    result = list(cur)
    conn.close()
    dep = [r[0] for r in result]
    return dep


def save_data(data, database_name):
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ")"

    def request(cur, cols):
        cur.execute("""INSERT INTO  """ + database_name + " " + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

    conn.commit()
    conn.close()


def load_pole_emploi_agencies(pool, table_name):
    data_token = get_pole_emploi_token()
    dep = get_dep_from_region("84")

    agencies = []
    for d in dep:
        agencies.append(get_pole_emploi_agencies(data_token["access_token"], d))
        time.sleep(1.1)

    agencies = pd.concat(agencies)
    agencies_zones = get_couples_from_agencies(agencies)

    agencies["year_data"] = "2023"
    agencies["year_cog"] = "2022"
    agencies = agencies.drop(columns=["zoneCompetences"])
    agencies = agencies.drop_duplicates(subset=["code"])

    agencies_zones["year_data"] = "2023"
    agencies_zones["year_cog"] = "2022"
    agencies_zones = agencies_zones.drop_duplicates()

    data = agencies

    cols_table = {
        "code": "VARCHAR(50) NOT NULL",
        "libelle": "VARCHAR(100) NULL",
        "libelleEtendu": "VARCHAR(250) NULL",
        "type": "VARCHAR(50) NULL",
        "typeAccueil": "VARCHAR(50) NULL",
        "email": "VARCHAR(50) NULL",
        "communeImplantation": "VARCHAR(50) NULL",
        "lat": "FLOAT NULL DEFAULT NULL",
        "lon": "FLOAT NULL DEFAULT NULL",

        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (code, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


def load_pole_emploi_agencies_zones(pool, table_name):
    data_token = get_pole_emploi_token()
    dep = get_dep_from_region("84")

    agencies = []
    for d in dep:
        agencies.append(get_pole_emploi_agencies(data_token["access_token"], d))
        time.sleep(1.1)

    agencies = pd.concat(agencies)
    agencies_zones = get_couples_from_agencies(agencies)

    agencies["year_data"] = "2023"
    agencies["year_cog"] = "2022"
    agencies = agencies.drop(columns=["zoneCompetences"])
    agencies = agencies.drop_duplicates(subset=["code"])

    agencies_zones["year_data"] = "2023"
    agencies_zones["year_cog"] = "2022"
    agencies_zones = agencies_zones.drop_duplicates()

    data = agencies_zones

    cols_table = {
        "code": "VARCHAR(50) NOT NULL",
        "zoneCompetences": "VARCHAR(50) NOT NULL",
        "year_data": "VARCHAR(12) NOT NULL",
        "year_cog": "VARCHAR(12) NOT NULL",
    }
    keys = "PRIMARY KEY (code, zoneCompetences, year_data) USING BTREE"

    load_database(pool, table_name, data, cols_table, keys)


def get_pole_emploi_work_access(token):
    r = requests.get("https://api.pole-emploi.io/partenaire/stats-perspectives-retour-emploi/v1/referentiel/territoires",
                     headers={
                         "Content-Type": "application/json",
                         "Accept": "application/json",
                         "Authorization": "Bearer " + data_token["access_token"]
                     },)
    print(r)
    datasets = r.json()
    print(datasets)
    territoires = pd.DataFrame(datasets["territoires"]) #, columns=["codeTypeTerritoire", "codeTerritoire", "libelleTerritoire"])
    print(territoires)
    print(territoires.groupby(by="codeTypeTerritoire").count())

    r = requests.get("https://api.pole-emploi.io/partenaire/stats-perspectives-retour-emploi/v1/referentiel/periodes",
                     headers={
                         "Content-Type": "application/json",
                         "Accept": "application/json",
                         "Authorization": "Bearer " + data_token["access_token"]
                     },)
    print(r)
    datasets = r.json()
    print(datasets)
    periodes = pd.DataFrame(datasets["periodes"]) #, columns=["codeTypeTerritoire", "codeTerritoire", "libelleTerritoire"])
    print(periodes)
    print(periodes.groupby(by="codeTypePeriode").count())

    r = requests.get("https://api.pole-emploi.io/partenaire/stats-perspectives-retour-emploi/v1/referentiel/type-activites",
                     headers={
                         "Content-Type": "application/json",
                         "Accept": "application/json",
                         "Authorization": "Bearer " + data_token["access_token"]
                     },)
    print(r)
    datasets = r.json()
    print(datasets)
    type_acti = pd.DataFrame(datasets["typeActivites"]) #, columns=["codeTypeTerritoire", "codeTerritoire", "libelleTerritoire"])
    print(type_acti)
    print(type_acti.groupby(by="codeTypeActivite").count())

    r = requests.post("https://api.pole-emploi.io/partenaire/stats-perspectives-retour-emploi/v1/indicateur/stat-acces-emploi",

                     headers={
                         "Content-Type": "application/json",
                         "Accept": "application/json",
                         "Authorization": "Bearer " + data_token["access_token"]
                     }, json={
            "codeTypeTerritoire": "EPCI",
            "codeTerritoire": "200041994",
            "codeTypeActivite": "ROME",
            "codeActivite": "A1203",
            "codeTypePeriode": "TRIMESTRE",
            "codeTypeNomenclature": "DUREEEMP"
        })
    print(r)
    datasets = r.json()
    print(datasets)
    periodes = pd.DataFrame(datasets["listeValeursParPeriode"]) #, columns=["codeTypeTerritoire", "codeTerritoire", "libelleTerritoire"])
    print(periodes)

    return datasets


if __name__ == '__main__':
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.max_rows', 60)
    pd.set_option('display.width', 1000)

    data_token = get_pole_emploi_token()
    print(data_token)

    get_pole_emploi_work_access(data_token)

    security = True
    if not security:
        load_pole_emploi_agencies(None, "pole_emploi_agencies")
        load_pole_emploi_agencies_zones(None, "pole_emploi_agencies_zones")

