from data_manager.database_connection.sql_connect import mariadb_connection
from compute_model.database_connection.database import engine
from sqlalchemy import text, bindparam


def db_request(request, params):
    result = None
    with engine.connect() as conn:
        t = text(request)
        for param, values in params.items():
            t = t.bindparams(bindparam(param, expanding=type(values) is list))
        result = conn.execute(t, params)
    return result


def save_to_db(pool, data, table_name):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ")"

    def request(cur, cols):
        cur.execute("INSERT INTO " + table_name + " " + cols_name + " VALUES " + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

    conn.commit()
    conn.close()

