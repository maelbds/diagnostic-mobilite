import math

from data_manager.database_connection.sql_connect import mariadb_connection


def exists_table(pool, table_name):
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_NAME = ?
    """, [table_name])
    result = list(cur)

    conn.commit()
    conn.close()

    return len(result) > 0


def create_table(cur, table_name, cols_table_request, keys):
    cur.execute("""CREATE TABLE IF NOT EXISTS """ + table_name + """ 
                        (
                        """ + cols_table_request + """, """ + keys + """
                        )
                        COLLATE 'utf8_general_ci'
                        """, [])


def request_table_insert_into(cur, table_name, cols_name, values_name, cols):
    cur.execute("INSERT INTO " + table_name + " " + cols_name + " VALUES " + values_name, cols)


def request_table_insert_into_many(cur, table_name, cols_name, values_name, data):
    l = len(data)
    memory_usage = data.memory_usage(index=False, deep=True).sum()
    memory_batch = 12000000
    batch_nb = math.ceil(memory_usage / memory_batch)
    batch_size = math.floor(l/batch_nb)

    for i in range(math.ceil(l/batch_size)):
        batch = data.iloc[i*batch_size:(i+1)*batch_size]
        batch = batch.to_numpy().tolist()
        cur.executemany(f"INSERT INTO {table_name} {cols_name} VALUES {values_name}", batch)


def load_database(pool, table_name, data, cols_table, keys):
    cols_table_request = ", ".join([name + " " + type for name, type in cols_table.items()])

    data = data[cols_table.keys()]
    cols_name = "(" + ", ".join([col for col in data.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ")"

    print(f"{table_name} - saving...")
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    create_table(cur, table_name, cols_table_request, keys)
    request_table_insert_into_many(cur, table_name, cols_name, values_name, data)
    """[request_table_insert_into(cur, table_name, cols_name, values_name, list(row.values))
     for index, row in data.iterrows()]"""

    conn.commit()
    conn.close()
    print(f"{table_name} - saved !")


def load_database_not_many(pool, table_name, data, cols_table, keys):
    cols_table_request = ", ".join([name + " " + type for name, type in cols_table.items()])

    data = data[cols_table.keys()]
    cols_name = "(" + ", ".join([col for col in data.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ")"

    print(f"{table_name} - saving...")
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    create_table(cur, table_name, cols_table_request, keys)
    #request_table_insert_into_many(cur, table_name, cols_name, values_name, data)
    [request_table_insert_into(cur, table_name, cols_name, values_name, list(row.values))
     for index, row in data.iterrows()]

    conn.commit()
    conn.close()
    print(f"{table_name} - saved !")


def empty_table(pool, table_name):
    print(f"{table_name} - emptying...")
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""TRUNCATE TABLE """ + table_name, [])
    conn.commit()
    conn.close()
    print(f"{table_name} - emptied !")


def create_new_table(pool, table_name, cols_table, keys):
    cols_table_request = ", ".join([name + " " + type for name, type in cols_table.items()])

    print(f"{table_name} - creating...")
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    create_table(cur, table_name, cols_table_request, keys)

    conn.commit()
    conn.close()
    print(f"{table_name} - created !")


def load_table(pool, table_name, data, cols_table):
    data = data[cols_table.keys()]
    cols_name = "(" + ", ".join([col for col in data.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ")"

    print(f"{table_name} - loading...")
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    request_table_insert_into_many(cur, table_name, cols_name, values_name, data)
    """[request_table_insert_into(cur, table_name, cols_name, values_name, list(row.values))
     for index, row in data.iterrows()]"""

    conn.commit()
    conn.close()
    print(f"{table_name} - loaded !")


if __name__ == '__main__':
    print(exists_table(None, "insee_communes"))
    print(exists_table(None, "table_unknown"))


