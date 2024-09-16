import pandas as pd

from api.resources.common.db_request import db_request


def get_all_districts():
    result = db_request(
        """ SELECT geo_code_district, geo_code_city
            FROM insee_arrondissements
        """,
        {}
    )
    districts = pd.DataFrame(result, columns=["geo_code_district", "geo_code_city"], dtype=str)
    return districts


def get_districts_to_city_dict():
    districts = get_all_districts()
    return districts.set_index("geo_code_district")["geo_code_city"].to_dict()


def add_districts(geo_codes):
    all_districts = get_all_districts()
    concerned_districts = all_districts.loc[all_districts["geo_code_city"].isin(geo_codes), "geo_code_district"].to_list()
    return geo_codes + concerned_districts


def get_districts(geo_codes):
    all_districts = get_all_districts()
    concerned_districts = all_districts.loc[all_districts["geo_code_city"].isin(geo_codes), "geo_code_district"].to_list()
    return concerned_districts


if __name__ == '__main__':
    print(get_districts_to_city_dict())

