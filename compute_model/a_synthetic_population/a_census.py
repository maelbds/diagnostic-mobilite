import pandas as pd

from compute_model.database_connection.db_request import db_request
from compute_model.years import COG, COG_census, year_census


def get_canton(geo_code):
    result = db_request(
        """ SELECT CV
            FROM insee_geo_communes
            WHERE CODGEO = :geo_code
            AND year_cog = :year_cog
        """,
        {
            "geo_code": geo_code,
            "year_cog": COG
        }
    )
    return result.scalar_one_or_none()


def get_census_from_canton(canton_code):
    result = db_request(
        """ SELECT id, id_census_hh, IPONDI, SEXE, AGED, csp, status, 
                   INPER, nb_child, hh_type, nb_car, TRANS, work_within_commune
            FROM insee_census 
            WHERE CANTVILLE = :canton_code 
            AND year_data = :year_data
            AND year_cog = :year_cog
        """,
        {
            "canton_code": canton_code,
            "year_data": year_census,
            "year_cog": COG_census,
        }
    )
    census = pd.DataFrame(result, columns=[
        "id_census_ind", "id_census_hh", "w_census_ind", "sexe", "age", "csp", "status",
        "nb_pers", "nb_child", "hh_type", "nb_car", "work_transport", "work_within_commune"], dtype=str)

    census = census.astype({"w_census_ind": "float64",
                            "sexe": "int32",
                            "age": "int32",
                            "csp": "int32",
                           "nb_pers": "int32",
                            "nb_child": "int32",
                            "nb_car": "int32",
                            "hh_type": "int32",
                            "work_within_commune": "int32"})
    return census


def get_census(geo_code):
    canton_code = get_canton(geo_code)
    census = get_census_from_canton(canton_code)
    return census


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    print(get_canton("69123"))
    print(get_census("79048"))
