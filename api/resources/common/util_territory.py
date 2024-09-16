import pandas as pd
from api.resources.common.db_request import db_request

from api.resources.common.util_flows_home_work import get_flows_home_work


def get_neighbors(geo_codes):
    result = db_request(
        """ SELECT geo_code_neighbor 
            FROM osm_adjacent 
            WHERE geo_code in :geo_codes 
            AND year_cog = :year_cog
        """,
        {
            "geo_codes": geo_codes,
            "year_cog": "2022"
        }
    )
    adjacent_communes = pd.DataFrame(result, columns=["geo_code"]).drop_duplicates()
    return [c for c in adjacent_communes["geo_code"] if c not in geo_codes]


def get_work_communes(geo_codes, influence_geocodes):
    flows = get_flows_home_work(geo_codes)

    geo_codes_work = flows["work_geo_code"].drop_duplicates().to_list()
    geo_codes_work = [g for g in geo_codes_work if g not in geo_codes and g not in influence_geocodes]

    return geo_codes_work


if __name__ == '__main__':
    print(get_neighbors(["79048"]))

