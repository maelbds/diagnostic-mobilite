import pandas as pd
import os
import ast

from api_diago.resources.common.db_request import db_request


def load_data_structures():
    """
    Read data from csv file & add it to the database
    :return:
    """
    cols = ["id",
            "siret",
            "rna",
            "nom",
            "adresse",
            "commune",
            "code_postal",
            "code_insee",
            "longitude",
            "latitude",
            "telephone", "courriel", "site_web", "lien_source",
            "presentation_resume",
            "presentation_detail",
            "source",
            #"antenne",
            #"labels_nationaux",
            "thematiques",
            "date_maj",
            "result_citycode"
            ]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    structures = pd.read_csv("data/structures-inclusion-2023-07-10.geocoded.csv",
                             usecols=cols, dtype=str)
    structures = structures[cols]

    structures["thematiques"] = structures["thematiques"].fillna("[]")
    structures["thematiques"] = [ast.literal_eval(t) for t in structures["thematiques"]]

    mask_no_code_insee = structures["code_insee"].isna()
    structures.loc[mask_no_code_insee, "code_insee"] = structures.loc[mask_no_code_insee, "result_citycode"]
    return structures


def load_data_services():
    """
    Read data from csv file & add it to the database
    :return:
    """
    cols = ["id",
            "structure_id",
            "source",

            "nom",
            "presentation_resume",
            "presentation_detail",

            #"types",
            "thematiques",

            #"adresse",
            #"commune",
            #"code_postal",
            "code_insee",

            "longitude",
            "latitude",

            #"telephone", "courriel", "lien_source",

            "zone_diffusion_type",
            "zone_diffusion_code",
            "zone_diffusion_nom",

            "date_maj",
            "date_suspension"
            ]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    services = pd.read_csv("data/services-inclusion-2023-07-10.csv", usecols=cols, dtype=str)
    services = services[cols]
    return services


if __name__ == '__main__':
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    structures = load_data_structures()
    print(structures)
    print(structures[structures["source"]=="dora"])
    print(structures.groupby(by="source").count())

    services = load_data_services()
    print(services)
    print(services[services["source"]=="dora"])
    print(services.groupby(by="source").count())

    mask_services_dora = services["source"] == "dora"
    services_dora = services[mask_services_dora]

    communes = db_request(None, """SELECT cog.COM, epci.EPCI, cog.DEP, cog.REG
                    FROM insee_cog_communes AS cog
                    LEFT JOIN insee_epci_communes AS epci ON cog.COM = epci.CODGEO
                    """, [])

    communes = pd.DataFrame(communes, columns=["geo_code", "epci", "dep", "reg"])
    print(communes)

    print(services)

    mask_zone_commune = services["zone_diffusion_type"] == "commune"
    mask_zone_epci = services["zone_diffusion_type"] == "epci"
    mask_zone_dep = services["zone_diffusion_type"] == "departement"
    mask_zone_reg = services["zone_diffusion_type"] == "region"

    services_com = services.loc[mask_zone_commune, ["id", "zone_diffusion_code"]].rename(columns={"zone_diffusion_code": "geo_code"})
    services_epci = pd.merge(services.loc[mask_zone_epci, ["id", "zone_diffusion_code"]], communes[["geo_code", "epci"]],
                             left_on="zone_diffusion_code", right_on="epci").drop(columns=["zone_diffusion_code", "epci"])
    services_dep = pd.merge(services.loc[mask_zone_dep, ["id", "zone_diffusion_code"]], communes[["geo_code", "dep"]],
                             left_on="zone_diffusion_code", right_on="dep").drop(columns=["zone_diffusion_code", "dep"])
    services_reg = pd.merge(services.loc[mask_zone_reg, ["id", "zone_diffusion_code"]], communes[["geo_code", "reg"]],
                             left_on="zone_diffusion_code", right_on="reg").drop(columns=["zone_diffusion_code", "reg"])
    print(services_epci)
    services_geo_codes = pd.concat([services_com, services_epci, services_reg, services_dep])
    print(services_geo_codes)

    geo_codes_by_services = services_geo_codes.groupby("id").agg(list)
    print(geo_codes_by_services)

    services_by_geo_codes = services_geo_codes.groupby("geo_code").agg(list)
    print(services_by_geo_codes)

    services = pd.merge(services, geo_codes_by_services, on="id", how="left")
    print(services)


    exit()

    print(services_dora)
    print(services_dora.groupby("structure_id").count())
    print(services_dora.groupby("zone_diffusion_type").count())
    print(sum(services_dora["zone_diffusion_type"].isna()))
    print(sum(services_dora["latitude"].isna()))
    print(pd.merge(services_dora, structures, left_on="structure_id", right_on="id"))



