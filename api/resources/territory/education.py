import pandas as pd
import numpy as np

from api.resources.common.cog import COG
from api.resources.common.log_stats import log_stats
from api.resources.common.util_territory import get_neighbors
from data_manager.sources.sources import get_years_for_source, get_label_link_for_source_year

from api.resources.common.db_request import db_request

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request

source_label = "educationdatagouv_schools"

dataset_education = {
    "endpoint": "territory/education",
    "is_mesh_element": False,
    "meshes": None,
    "name_year": "EducationDataGouv",
    "years": get_years_for_source(source_label),
}


def get_schools(geo_codes, year):
    result = db_request(
        """SELECT e.id, p.CODGEO_DES, 
                types.name, e.name,
                e.lat, e.lon 
            FROM educationdatagouv_schools AS e
            JOIN insee_passage_cog AS p ON e.geo_code = p.CODGEO_INI
            
            JOIN educationdatagouv_schools_types AS t ON e.id_type = t.id
            JOIN types ON t.id_type = types.id
            
            WHERE p.CODGEO_DES IN :geo_codes
            AND e.year_data = :year_data
            AND t.to_keep = 1 
            AND p.year_cog = :cog
        """,
        {
            "geo_codes": geo_codes,
            "year_data": year,
            "cog": COG
        }
    )

    schools = pd.DataFrame(result, columns=["id", "geo_code",
                                            "type", "name",
                                            "lat", "lon"])
    return schools


def get_universities(geo_codes, year):
    result = db_request(
        """SELECT univ.id, p.CODGEO_DES,
                types.name, univ_types.name_univ_type, 
                univ.lat, univ.lon 
            FROM esrdatagouv_universities AS univ 
            JOIN insee_passage_cog AS p ON univ.geo_code = p.CODGEO_INI
            
            JOIN esrdatagouv_universities_types AS univ_types ON univ.code_type = univ_types.id_univ_type
            JOIN types  ON univ_types.id_type = types.id
            JOIN categories ON types.id_category = categories.id
            JOIN reasons ON categories.id_reason = reasons.id
            
            WHERE p.CODGEO_DES IN :geo_codes
            AND univ.year_data = :year_data
            AND p.year_cog = :cog
        """,
        {
            "geo_codes": geo_codes,
            "year_data": year,
            "cog": COG
        }
    )
    universities = pd.DataFrame(result, columns=["id", "geo_code",
                                                 "type", "name",
                                                 "lat", "lon"])
    return universities


def format_places(places):
    places.dropna(subset=["lat", "lon"], inplace=True)
    places["coords_geo"] = [[lon, lat] for lat, lon in zip(places["lat"], places["lon"])]
    places.drop(columns=["lat", "lon"], inplace=True)
    places["name"] = [p.title() for p in places["name"]]
    return places


def get_education(geo_codes, year):
    sources = [get_label_link_for_source_year(name, year) for name in [source_label]] + \
              [get_label_link_for_source_year("esrdatagouv_universities", "2017")]

    influence_geocodes = get_neighbors(geo_codes)
    all_geocodes = geo_codes + influence_geocodes

    schools = get_schools(all_geocodes, year)
    universities = get_universities(all_geocodes, get_years_for_source("esrdatagouv_universities")[0])

    places = format_places(pd.concat([schools, universities]))

    places = places.replace({np.nan: None})

    return {
        "elements": {
            "education": {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {
                        "coordinates": coords,
                        "geo_code": geo_code,
                        "name": name,
                        "type": type,
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": coords
                    }
                } for coords, name, type, geo_code in zip(
                    places["coords_geo"],
                    places["name"],
                    places["type"],
                    places["geo_code"],
                )]
            }},
        # "legend": legend.to_dict(orient="list"),
        "sources": sources,
        "is_mesh_element": False
    }


class Education(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes
        year = perimeter.year

        log_stats("education", geo_codes, None, year)
        message_request("education", geo_codes)
        return get_education(geo_codes, year)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    print(get_education(["13055"], "2024"))
