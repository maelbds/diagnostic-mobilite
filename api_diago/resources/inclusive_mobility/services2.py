import pandas as pd
import numpy as np
import ast
import requests

from data_manager.data_inclusion.source import SOURCE_DATA_INCLUSION

from api_diago.resources.common.db_request import db_request

from flask_restful import Resource

from api_diago.resources.common.log_message import message_request
from api_diago.resources.common.schema_request import perimeter_request
from data_manager.data_inclusion.save_data_inclusion import cols_structures, cols_services
from api_diago.resources.inclusive_mobility.keys import DATAINCLUSION_TOKEN as token


all_communes = db_request("""SELECT cog.COM, epci.EPCI, cog.DEP, cog.REG
                FROM insee_cog_communes AS cog
                LEFT JOIN insee_epci_communes AS epci ON cog.COM = epci.CODGEO
                """, {})

all_communes = pd.DataFrame(all_communes, columns=["geo_code", "epci", "dep", "reg"])


def get_di_services(sources, geo_codes, thematiques):
    all_services = []
    all_structures = []

    communes = pd.DataFrame({"geo_code": geo_codes})
    communes = pd.merge(communes, all_communes[["geo_code", "dep"]], on="geo_code", how="left")

    deps = communes["dep"].drop_duplicates().to_list()

    for dep in deps:
        for source in sources:
            for thematique in thematiques:
                print(dep)
                sources_r = "&".join([f"sources={s}" for s in sources])
                thematiques_r = "&".join([f"thematiques={t}" for t in thematiques])

                r = requests.get(
                    f"https://api.data.inclusion.beta.gouv.fr/api/v0/services?departement={dep}"
                    f"&thematique={thematique}&source={source}",
                          #&{thematiques_r}&distance=0", #{sources_r}&"
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Bearer {token}"
                    }, )
                datasets = r.json()
                items = datasets["items"]
                #print(items)

                services = pd.DataFrame(items)
                services = services[["id", "structure_id", "nom", "adresse",
                                     "commune", "code_postal", "code_insee", "longitude", "latitude",
                                     "telephone", "courriel", "lien_source",
                                     "thematiques",
                                     "presentation_resume",
                                     "presentation_detail",
                                     "zone_diffusion_type",
                                     "zone_diffusion_code",
                                     "zone_diffusion_nom",
                                     "source", "date_maj", "date_suspension"]]

                mask_diffusion_pays = services["zone_diffusion_type"] == "pays"
                services = services.loc[~mask_diffusion_pays]

                #services["geo_code"] = geo_code
                #services["thematiques"] = [ast.literal_eval(t) for t in services["thematiques"]]

                """structures = pd.DataFrame([item["structure"] for item in items]).drop_duplicates(subset=["id"])
                structures = structures[["id", "siret", "nom", "commune", "adresse", "code_postal", "code_insee",
                                         "longitude", "latitude",
                                         "telephone", "courriel", "lien_source", "site_web",
                                         "presentation_resume",
                                         "presentation_detail",
                                         "thematiques",
                                         "source", "date_maj", "antenne"]]
                mask_in_services = structures["id"].isin(services["structure_id"])
                structures = structures.loc[mask_in_services]"""
                structures = pd.DataFrame()

                all_services.append(services)
                all_structures.append(structures)

    services = pd.concat(all_services).drop_duplicates(subset="id")
    structures = pd.concat(all_structures).drop_duplicates()

    # finding geocodes for diffusion zone
    mask_zone_commune = services["zone_diffusion_type"] == "commune"
    mask_zone_epci = services["zone_diffusion_type"] == "epci"
    mask_zone_dep = services["zone_diffusion_type"] == "departement"
    mask_zone_reg = services["zone_diffusion_type"] == "region"

    services_com = services.loc[mask_zone_commune, ["id", "zone_diffusion_code"]].rename(
        columns={"zone_diffusion_code": "geo_code"})
    services_epci = pd.merge(services.loc[mask_zone_epci, ["id", "zone_diffusion_code"]],
                             all_communes[["geo_code", "epci"]],
                             left_on="zone_diffusion_code", right_on="epci", how="left").drop(
        columns=["zone_diffusion_code", "epci"])
    services_dep = pd.merge(services.loc[mask_zone_dep, ["id", "zone_diffusion_code"]], all_communes[["geo_code", "dep"]],
                            left_on="zone_diffusion_code", right_on="dep", how="left").drop(columns=["zone_diffusion_code", "dep"])
    services_reg = pd.merge(services.loc[mask_zone_reg, ["id", "zone_diffusion_code"]], all_communes[["geo_code", "reg"]],
                            left_on="zone_diffusion_code", right_on="reg", how="left").drop(columns=["zone_diffusion_code", "reg"])

    services_geo_codes = pd.concat([services_com, services_epci, services_reg, services_dep])
    services_geo_codes = services_geo_codes.groupby("geo_code", as_index=False).agg(**{
        "id": pd.NamedAgg("id", list)
    })
    mask_concerned_com = services_geo_codes["geo_code"].isin(geo_codes)
    services_geo_codes = services_geo_codes.loc[mask_concerned_com]
    services_geo_codes["number services"] = [len(id) for id in services_geo_codes["id"]]


    print(services)
    print(structures)
    print(services_geo_codes)


def get_services(geo_codes):
    result = db_request(
        """ SELECT *
            FROM datainclusion_services AS s
            JOIN datainclusion_services_geocodes AS g ON s.id = g.id
            WHERE g.geo_code IN :geo_codes
            AND s.year_data = :year_di
        """,
        {
            "geo_codes": geo_codes,
            "year_di": SOURCE_DATA_INCLUSION
        }
    )

    services = pd.DataFrame(result, columns=cols_services + ["year_data", "year_cog", "id_bis", "geo_code"])
    services = services.drop_duplicates(subset=["id"]).drop(columns=["id_bis", "geo_code"])

    services["thematiques"] = [ast.literal_eval(t) for t in services["thematiques"]]
    services["date_maj"] = services["date_maj"].astype(str)
    services["date_suspension"] = services["date_suspension"].astype(str)

    services = services.replace({np.nan: None})

    return {
        "services": services.to_dict(orient="list")
    }


def get_services_geocodes(geo_codes):
    result = db_request(
        """ SELECT id, geo_code
            FROM datainclusion_services_geocodes 
            WHERE geo_code IN :geo_codes
        """,
        {
            "geo_codes": geo_codes
        }
    )

    services = pd.DataFrame(result, columns=["structure_id", "geo_code"])
    services = services.groupby("geo_code", as_index=False).agg(list)

    services = pd.merge(pd.DataFrame({"geo_code": geo_codes}), services, on="geo_code", how="left")
    services = services.replace({np.nan: None})

    return {
        "services_geocodes": services.to_dict(orient="list")
    }


class Services(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("services", geo_codes)
        return get_services(geo_codes)


class ServicesGeocodes(Resource):
    def post(self):
        perimeter = perimeter_request.parse()
        geo_codes = perimeter.geo_codes

        message_request("services geocodes", geo_codes)
        return get_services_geocodes(geo_codes)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 2000)
    get_di_services(["dora"], ["79048", "79191", '39283', "25056"], ["mobilite"])

    #af77f6bd-4cf7-4cba-9f5f-409f554b014b


"""


    result = db_request(
        """""" SELECT geo_code, centroid_lat, centroid_lon
            FROM ign_commune_center
            WHERE geo_code IN :geo_codes
        """""",
        {
            "geo_codes": geo_codes
        }
    )
    communes = pd.DataFrame(result, columns=["geo_code", "lat", "lon"]).set_index("geo_code")

    # Geo to Lambert93 coordinates system :
    transformer2154 = Transformer.from_crs("epsg:4326",  # World Geodetic System (lat/lon)
                                           "epsg:2154")  # Lambert 93 (x, y)

    def geo_to_lambert(lat, lon):
        x, y = transformer2154.transform(lat, lon)
        return np.array([round(x), round(y)])

    communes["coords_lamb"] = [geo_to_lambert(lat, lon) for lat, lon in zip(communes["lat"], communes["lon"])]
    communes["x"] = [c[0] for c in communes["coords_lamb"]]
    communes["y"] = [c[1] for c in communes["coords_lamb"]]

    radius = 80 * 1000

    avg_x = (communes["x"].max() + communes["x"].min())/2
    avg_y = (communes["y"].max() + communes["y"].min())/2

    min_x = communes["x"].min() + radius
    max_x = communes["x"].max() - radius

    if max_x < min_x:
        intervals_x = [avg_x]
    else:
        intervals_x = np.append(np.arange(min_x, max_x, radius*2), max_x)

    min_y = communes["y"].min() + radius
    max_y = communes["y"].max() - radius

    if max_y < min_y:
        intervals_y = [avg_y]
    else:
        intervals_y = np.append(np.arange(min_y, max_y, radius*2), max_y)

    centroids = sum([[np.array([x, y]) for x in intervals_x] for y in intervals_y], [])
    distances = [[np.linalg.norm(c - centroid) for c in communes["coords_lamb"]] for centroid in centroids]

    centroids_communes = list(set([pd.Series(dist, index=communes.index).idxmin() for dist in distances]))


"""