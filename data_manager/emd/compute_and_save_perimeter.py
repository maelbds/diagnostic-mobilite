import pandas as pd

from compute_model.database_connection.db_request import db_request
from data_manager.db_functions import load_database


def compute_perimeter(emd_id):
    result = db_request(
        """SELECT  g.emd_id, g.id, g.geo_code

           FROM emd_geo AS g

           WHERE g.emd_id = :emd_id 
        """,
        {
            "emd_id": emd_id
        })

    geo = pd.DataFrame(result, columns=["emd_id", "id", "geo_code"])
    mask_perimeter = geo["id"].astype(int) < 100000

    perimeter = geo.loc[mask_perimeter, ["emd_id", "geo_code"]]
    perimeter = perimeter.drop_duplicates()

    return perimeter


def load_emd_perimeter(pool, emd_id):
    table_name = "emd_perimeter"
    cols_table = {
        "emd_id": "VARCHAR(50) NOT NULL",
        "geo_code": "VARCHAR(50) NOT NULL"
    }
    keys = "PRIMARY KEY (emd_id, geo_code) USING BTREE"

    data = compute_perimeter(emd_id)
    load_database(pool, table_name, data, cols_table, keys)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    security = False
    if not security:
        load_emd_perimeter(None, "montpellier")

