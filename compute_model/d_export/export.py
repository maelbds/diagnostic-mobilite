import pandas as pd
import numpy as np
import os
from compute_model.v_database_connection.db_request import db_request


def get_travels():
    regions = ["84", "93", "94", "11", "24", "27", "28", "32", "44", "52", "53", "75", "76"]

    for region in regions:
        result = db_request(
            """ SELECT id_ind, id_trav, trav_nb, w_trav,
                           geo_code,
                           mode,
                           reason_ori, reason_des,
                           distance,
                           geo_code_ori, geo_code_des,
                           source_id, distance_emp
                FROM computed_travels
                LEFT JOIN insee_cog_communes AS cog ON computed_travels.geo_code = cog.COM
                WHERE cog.REG = :region
            """,
            {
                "region": region
            }
        )
        print(f"result region {region} - {result.rowcount}")

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)
        i = 0

        for p in result.partitions(1000000):
            travels = pd.DataFrame(p, columns=["id_ind", "id_trav", "trav_nb", "w_trav",
                                               "geo_code",
                                               "mode",
                                               "reason_ori", "reason_des",
                                               "distance",
                                               "geo_code_ori", "geo_code_des",
                                               "source_id", "distance_emp"])
            print(f" -- partition {i}")
            print(travels)

            travels.to_csv(f"data/travels_{region}.csv", index=False,
                           mode="w" if i == 0 else "a",
                           header=i == 0)
            i += 1


if __name__ == '__main__':
    get_travels()
