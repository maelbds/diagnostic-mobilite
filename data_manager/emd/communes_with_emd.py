import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.insee_general.districts import list_district_to_city


def get_communes_with_emd(pool):
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    cur.execute("""SELECT 
                   emd_geo.geo_code, emd_persons.w_ind
                   FROM emd_persons
                   JOIN emd_geo ON emd_persons.ra_id = emd_geo.id AND emd_persons.emd_id = emd_geo.emd_id
                   """, [])
    result = list(cur)
    result = pd.DataFrame(result, columns=["geo_code", "population"])
    conn.close()

    communes_with_emd = result.groupby("geo_code", as_index=False).sum()
    if __name__ == '__main__':
        print(communes_with_emd)

    covered_geo_codes = communes_with_emd["geo_code"].to_list()
    covered_geo_codes = list_district_to_city(pool, covered_geo_codes).to_list()
    return covered_geo_codes


def are_communes_covered_by_emd(pool, geo_codes):
    covered_communes = get_communes_with_emd(pool)
    return all([geo_code in covered_communes for geo_code in geo_codes])



# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    print(get_communes_with_emd(None))

    print(are_communes_covered_by_emd(None, ['13001', '13002', '13003', '13005', '13007', '13008', '13009', '13012', '13013', '13014', '13015', '13016', '13019', '13020', '13021', '13022', '13023', '13024', '13025', '13026', '13028', '13029', '13030', '13031', '13032', '13033', '13035', '13037', '13039', '13040', '13041', '13042', '13043', '13044', '13046', '13047', '13048', '13049', '13050', '13051', '13053', '13054', '13055', '13056', '13059', '13060', '13062', '13063', '13069', '13070', '13071', '13072', '13073', '13074', '13075', '13077', '13078', '13079', '13080', '13081', '13082', '13084', '13085', '13086', '13087', '13088', '13090', '13091', '13092', '13093', '13095', '13098', '13099', '13101', '13102', '13103', '13104', '13105', '13106', '13107', '13109', '13110', '13111', '13112', '13113', '13114', '13115', '13117', '13118', '13119', '83120', '84089']
))







