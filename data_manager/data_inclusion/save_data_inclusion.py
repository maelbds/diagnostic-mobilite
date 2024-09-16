import ast

import pandas as pd
import os
import numpy as np

from data_manager.db_functions import load_database, create_new_table, empty_table, load_table
from data_manager.utilities import download_url
from api_diago.resources.common.db_request import db_request

from datetime import date


def download_files():
    # reference : "https://www.data.gouv.fr/fr/datasets/referentiel-de-loffre-dinsertion-liste-des-structures-et-services-dinsertion/"
    files = [{
        "name": "Structures inclusion",
        "url": "https://www.data.gouv.fr/fr/datasets/r/fd4cb3ef-5c31-4c99-92fe-2cd8016c0ca5",
        "dir": "data",
        "file_name": "structures.csv",
    },{
        "name": "Services inclusion",
        "url": "https://www.data.gouv.fr/fr/datasets/r/5abc151a-5729-4055-b0a9-d5691276f461",
        "dir": "data",
        "file_name": "services.csv",
    }]

    for file in files:
        file_path = f"{file['dir']}/{file['file_name']}"

        if not os.path.isfile(file_path):
            print(f"{file['name']} - downloading")
            download_url(file['url'], file_path)
        else:
            print(f"{file['name']} - already downloaded")


cols_structures = ["id",
                   # "siret",
                   # "rna",
                   "nom",
                   "adresse",
                   "commune",
                   "code_postal",
                   "code_insee",
                   "_di_geocodage_code_insee",
                   "longitude",
                   "latitude",
                   "telephone", "courriel", "lien_source", "site_web",
                   "presentation_resume",
                   "presentation_detail",
                   "source",
                   # "antenne",
                   # "labels_nationaux",
                   "thematiques",
                   "date_maj"
                   ]

cols_services = [
    "id",
    "structure_id",
    "source",

    "nom",
    "lien_source",
    "presentation_resume",
    "presentation_detail",

    # "types",
    "thematiques",

    # "adresse",
    # "commune",
    # "code_postal",
    "code_insee",

    "longitude",
    "latitude",

    # "telephone", "courriel",

    "zone_diffusion_type",
    "zone_diffusion_code",
    "zone_diffusion_nom",

    "date_maj",
    "date_suspension"
]


def handle_datainclusion():
    # STRUCTURES
    structures = pd.read_csv("data/structures.csv", usecols=cols_structures, dtype=str)
    structures = structures[cols_structures]

    # add missing thematiques thanks to services info
    services = pd.read_csv("data/services.csv", usecols=["structure_id", "thematiques"], dtype=str)
    services = services[["structure_id", "thematiques"]]
    services["thematiques"] = services["thematiques"].fillna("[]")
    services["thematiques"] = [ast.literal_eval(t) for t in services["thematiques"]]
    services = services.groupby("structure_id", as_index=False).sum().rename(
        columns={"thematiques": "thematiques_services"})

    structures["thematiques"] = structures["thematiques"].fillna("[]")
    structures["thematiques"] = [ast.literal_eval(t) for t in structures["thematiques"]]
    structures = pd.merge(structures, services, how="left", left_on="id", right_on="structure_id")
    mask_thematique_list = [type(t) is list for t in structures["thematiques"]]
    structures = structures.loc[mask_thematique_list]
    structures["thematiques"] = [list(set(t + t_s)) if type(t_s) is list else t
                                 for t, t_s in zip(structures["thematiques"], structures["thematiques_services"])]
    structures = structures.drop(columns=["structure_id", "thematiques_services"])
    structures["thematiques"] = structures["thematiques"].apply(lambda t: "[" + ",".join(["'" + s + "'" for s in t]) + "]")

    # filling geo_code
    mask_no_code_insee = structures["code_insee"].isna()
    structures.loc[mask_no_code_insee, "code_insee"] = structures.loc[mask_no_code_insee, "_di_geocodage_code_insee"]
    structures = structures.drop(columns=["_di_geocodage_code_insee"])

    structures = structures.drop_duplicates(subset="id")
    structures = structures.replace({np.nan: None})
    structures["nom"] = structures["nom"].apply(lambda x: x[:249] if x is not None else None)
    structures["thematiques"] = structures["thematiques"].fillna("[]")
    structures["saved_on"] = date.today()

    # set new index
    structures["new_id"] = structures.index
    new_id_table = structures[["id", "new_id"]].set_index("id")
    structures = structures.drop(columns="id").rename(columns={"new_id": "id"})
    print(structures)


    # SERVICES
    services = pd.read_csv("data/services.csv", usecols=cols_services, dtype=str)
    services = services[cols_services]

    services["thematiques"] = services["thematiques"].fillna("[]")

    services = services.drop_duplicates(subset="id")
    services = services.replace({np.nan: None})

    services["saved_on"] = date.today()

    # reindexing structure id
    services = pd.merge(services, new_id_table, left_on="structure_id", right_index=True)
    services = services.drop(columns=["structure_id"]).rename(columns={"new_id": "structure_id"})

    # set new index
    services["id"] = services.index
    print(services)

    # finding geocodes for diffusion zone
    communes = db_request(None, """SELECT cog.COM, epci.EPCI, cog.DEP, cog.REG
                    FROM insee_cog_communes AS cog
                    LEFT JOIN insee_epci_communes AS epci ON cog.COM = epci.CODGEO
                    """, [])
    communes = pd.DataFrame(communes, columns=["geo_code", "epci", "dep", "reg"])

    mask_zone_commune = services["zone_diffusion_type"] == "commune"
    mask_zone_epci = services["zone_diffusion_type"] == "epci"
    mask_zone_dep = services["zone_diffusion_type"] == "departement"
    mask_zone_reg = services["zone_diffusion_type"] == "region"

    services_com = services.loc[mask_zone_commune, ["id", "zone_diffusion_code"]].rename(
        columns={"zone_diffusion_code": "geo_code"})
    services_epci = pd.merge(services.loc[mask_zone_epci, ["id", "zone_diffusion_code"]],
                             communes[["geo_code", "epci"]],
                             left_on="zone_diffusion_code", right_on="epci").drop(
        columns=["zone_diffusion_code", "epci"])
    services_dep = pd.merge(services.loc[mask_zone_dep, ["id", "zone_diffusion_code"]], communes[["geo_code", "dep"]],
                            left_on="zone_diffusion_code", right_on="dep").drop(columns=["zone_diffusion_code", "dep"])
    services_reg = pd.merge(services.loc[mask_zone_reg, ["id", "zone_diffusion_code"]], communes[["geo_code", "reg"]],
                            left_on="zone_diffusion_code", right_on="reg").drop(columns=["zone_diffusion_code", "reg"])

    services_geo_codes = pd.concat([services_com, services_epci, services_reg, services_dep])
    services_geo_codes.dropna(inplace=True)
    services_geo_codes.drop_duplicates(inplace=True)
    print(services_geo_codes)

    return structures, services, services_geo_codes


def load_datainclusion(pool):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    download_files()

    data_structures, data_services, data_services_geocodes = handle_datainclusion()

    # structures
    cols_table = {
        "id": "VARCHAR(255) NOT NULL COLLATE 'utf8_bin'",
        "nom": "VARCHAR(255) NULL",
        "adresse": "VARCHAR(250) NULL",
        "commune": "VARCHAR(150) NULL",
        "code_postal": "VARCHAR(50) NULL",
        "code_insee": "VARCHAR(50) NULL",
        "longitude": "FLOAT NULL DEFAULT NULL",
        "latitude": "FLOAT NULL DEFAULT NULL",
        "telephone": "VARCHAR(50) NULL",
        "courriel": "VARCHAR(100) NULL",
        "site_web": "TEXT NULL",
        "lien_source": "TEXT NULL",
        "presentation_resume": "TEXT NULL COLLATE 'utf8mb4_unicode_ci'",
        "presentation_detail": "TEXT NULL COLLATE 'utf8mb4_unicode_ci'",
        "source": "VARCHAR(50) NULL",
        "thematiques": "TEXT NULL",
        "date_maj": "DATE NULL",

        "saved_on": "DATE NULL",
    }
    keys = "PRIMARY KEY (id) USING BTREE, KEY (code_insee) USING BTREE"
    table_name = "datainclusion_structures"

    create_new_table(pool, table_name, cols_table, keys)
    empty_table(pool, table_name)
    load_table(pool, table_name, data_structures, cols_table)

    # services
    cols_table = {
        "id": "VARCHAR(255) NOT NULL COLLATE 'utf8_bin'",
        "structure_id": "VARCHAR(255) NOT NULL COLLATE 'utf8_bin'",
        "source": "VARCHAR(50) NULL",
        "nom": "VARCHAR(255) NULL COLLATE 'utf8mb4_unicode_ci'",
        "lien_source": "TEXT NULL DEFAULT NULL",
        "presentation_resume": "TEXT NULL COLLATE 'utf8mb4_unicode_ci'",
        "presentation_detail": "TEXT NULL COLLATE 'utf8mb4_unicode_ci'",
        "thematiques": "TEXT NULL",
        "code_insee": "VARCHAR(50) NULL",
        "longitude": "FLOAT NULL DEFAULT NULL",
        "latitude": "FLOAT NULL DEFAULT NULL",
        "zone_diffusion_type": "VARCHAR(50) NULL",
        "zone_diffusion_code": "VARCHAR(50) NULL",
        "zone_diffusion_nom": "VARCHAR(100) NULL",
        "date_maj": "DATE NULL",
        "date_suspension": "DATE NULL",

        "saved_on": "DATE NULL",
    }
    keys = "PRIMARY KEY (id) USING BTREE, KEY (code_insee) USING BTREE, KEY (structure_id) USING BTREE"
    table_name = "datainclusion_services"

    create_new_table(pool, table_name, cols_table, keys)
    empty_table(pool, table_name)
    load_table(pool, table_name, data_services, cols_table)

    # services_geocodes
    cols_table = {
        "id": "VARCHAR(255) NOT NULL COLLATE 'utf8_bin'",
        "geo_code": "VARCHAR(10) NOT NULL",
    }
    keys = "PRIMARY KEY (id, geo_code) USING BTREE, KEY (geo_code) USING BTREE"
    table_name = "datainclusion_services_geocodes"

    create_new_table(pool, table_name, cols_table, keys)
    empty_table(pool, table_name)
    load_table(pool, table_name, data_services_geocodes, cols_table)

    os.remove("data/structures.csv")
    os.remove("data/services.csv")


if __name__ == '__main__':
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    #print(handle_datainclusion())

    load_datainclusion(None)
