import pandas as pd
import os
import numpy as np

from api.resources.common.db_request import db_request
from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.db_functions import create_new_table


def create_table_sources(pool):
    table_name = "sources"

    cols_table = {
        "id": "VARCHAR(50) NOT NULL",
        "name": "VARCHAR(50) NOT NULL",
        "table_name": "VARCHAR(50) NOT NULL",
        "label": "VARCHAR(250) NOT NULL",
        "link": "TEXT NULL DEFAULT NULL",
        "reference": "TEXT NULL DEFAULT NULL",
        "year_data": "VARCHAR(50) NULL DEFAULT NULL",
        "year_cog": "VARCHAR(50) NULL DEFAULT NULL",
    }
    keys = "PRIMARY KEY (id) USING BTREE"

    create_new_table(pool, table_name, cols_table, keys)


def saved_sources_for_table(table_name):
    result = db_request(
        """ SELECT *
            FROM sources
            WHERE table_name = :table_name
            """,
        {
            "table_name": table_name
        }
    )

    data = pd.DataFrame(result, columns=["id", "name", "table_name", "label", "link", "reference",
                                         "year_data", "year_cog"], dtype=str)
    return data


def req_sources_for_table(table_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    required_sources = pd.read_csv("required_sources.csv", delimiter=";", dtype=str)
    required_sources = required_sources.dropna(subset=["id"]).replace({np.nan: None})
    mask_table = required_sources["table_name"] == table_name
    return required_sources.loc[mask_table]


def missing_sources_for_table(table_name):
    req_sources = req_sources_for_table(table_name)
    saved_sources = saved_sources_for_table(table_name)
    mask_missing = ~req_sources['id'].isin(saved_sources["id"])
    return req_sources.loc[mask_missing]


def get_years_for_source(source_name):
    result = db_request(
        """ SELECT *
            FROM sources
            WHERE table_name = :table_name
            """,
        {
            "table_name": source_name
        }
    )

    data = pd.DataFrame(result, columns=["id", "name", "table_name", "label", "link", "reference",
                                         "year_data", "year_cog"], dtype=str)
    return data["year_data"].drop_duplicates().to_list()


def get_label_link_for_source_year(source_name, source_year):
    result = db_request(
        """ SELECT label, reference
            FROM sources
            WHERE table_name = :table_name
            AND year_data = :year
            """,
        {
            "table_name": source_name,
            "year": source_year
        }
    )

    label, link = result.first()
    return {"label": label, "link": link}


def save_source(pool, id, name, table_name, label, link, reference, year_data, year_cog):
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    cur.execute("""INSERT INTO sources (id, name, table_name, label, link, reference, year_data, year_cog)
                VALUES (?,?,?,?,?,?,?,?) """,
        (id, name, table_name, label, link, reference, year_data, year_cog)
    )

    conn.commit()
    conn.close()


if __name__ == '__main__':
    missing_sources_for_table("insee_cog_communes")

