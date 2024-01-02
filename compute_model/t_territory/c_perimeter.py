import pandas as pd

from compute_model.v_database_connection.db_request import db_request
from compute_model.t_territory.d_flows_home_work import WORK_FLOWS_THRESHOLD_FLOW, get_flows_home_work
from compute_model.sources import sources


def get_influence_communes_geo_codes(geo_codes):
    result = db_request(
        """ SELECT geo_code_neighbor 
            FROM osm_adjacent 
            WHERE geo_code in :geo_codes AND year_cog = :year_cog
        """,
        {
            "geo_codes": geo_codes,
            "year_cog": sources["adjacent"]["year"]
        }
    )
    adjacent_communes = pd.DataFrame(result, columns=["geo_code"]).drop_duplicates()
    return [c for c in adjacent_communes["geo_code"] if c not in geo_codes]


def get_work_communes_geo_codes(geo_codes, geo_codes_influence, flows):
    flows_work = flows.groupby(by=["home_geo_code", "work_geo_code"], as_index=False).sum()
    mask_significant_flows = flows_work["flow"] > WORK_FLOWS_THRESHOLD_FLOW
    flows_work = flows_work.loc[mask_significant_flows]

    geo_codes_work = flows_work["work_geo_code"].drop_duplicates().to_list()
    geo_codes_work = [g for g in geo_codes_work if g not in geo_codes and g not in geo_codes_influence]

    return geo_codes_work


if __name__ == '__main__':
    print(get_influence_communes_geo_codes(["79048", "79128"]))

    geo_codes_test = ["79048", "79128"]
    flows_home_work = get_flows_home_work(geo_codes_test)

    print(get_work_communes_geo_codes(geo_codes_test, [], flows_home_work))

