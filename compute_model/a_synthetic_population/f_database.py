import pandas as pd
import numpy as np

from compute_model.database_connection.db_request import save_to_db, db_request
from data_manager.db_functions import create_new_table


def create_table_syn_pop(pool):
    table_name = "computed_syn_pop"
    cols_table = {
        "geo_code": "VARCHAR(12) NOT NULL",
        "id_census_ind": "INT(11) NOT NULL",
        "weights": "INT(5) NOT NULL",
    }
    keys = "PRIMARY KEY (geo_code, id_census_ind) USING BTREE, KEY(geo_code) USING BTREE"

    create_new_table(pool, table_name, cols_table, keys)


def create_table_syn_pop_quality(pool):
    table_name = "computed_syn_pop_quality"
    cols_table = {
        "geo_code": "VARCHAR(12) NOT NULL",
        "rel_diff_mean": "FLOAT NULL",
        "pond_rel_diff_mean": "FLOAT NULL",
        "rel_diff_max": "FLOAT NULL",
        "rel_diff_max_marginal": "FLOAT NULL",

        "rel_diff_mean_30": "FLOAT NULL",
        "pond_rel_diff_mean_30": "FLOAT NULL",
        "rel_diff_max_30": "FLOAT NULL",
        "rel_diff_max_marginal_30": "FLOAT NULL",

        "rel_diff_mean_50": "FLOAT NULL",
        "pond_rel_diff_mean_50": "FLOAT NULL",
        "rel_diff_max_50": "FLOAT NULL",
        "rel_diff_max_marginal_50": "FLOAT NULL",

        "rel_diff_mean_100": "FLOAT NULL",
        "pond_rel_diff_mean_100": "FLOAT NULL",
        "rel_diff_max_100": "FLOAT NULL",
        "rel_diff_max_marginal_100": "FLOAT NULL",
    }
    keys = "PRIMARY KEY (geo_code) USING BTREE"

    create_new_table(pool, table_name, cols_table, keys)


def save_synthetic_population(geo_code, census_weighted):
    mask_null_weight = census_weighted["weights"] == 0
    census_weighted = census_weighted.loc[~mask_null_weight, ["id_census_ind", "weights"]]
    census_weighted["geo_code"] = geo_code
    save_to_db(None, census_weighted, "computed_syn_pop")
    return


def save_synthetic_population_quality(geo_code, quality):
    quality["geo_code"] = geo_code
    quality = quality.replace({np.nan: None})
    save_to_db(None, quality, "computed_syn_pop_quality")
    return


def get_saved_geo_codes():
    result = db_request(
        """ SELECT geo_code
            FROM computed_syn_pop_quality
        """,
        {}
    )
    syn_pop = pd.DataFrame(result, columns=["geo_code"])
    return syn_pop["geo_code"].drop_duplicates().to_list()


if __name__ == '__main__':
    create_table_syn_pop(None)
    create_table_syn_pop_quality(None)

