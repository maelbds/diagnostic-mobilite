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


def load_database(pool, table_name, data, cols_table, keys):
    cols_table_request = ", ".join([name + " " + type for name, type in cols_table.items()])

    data = data[cols_table.keys()]
    cols_name = "(" + ", ".join([col for col in data.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ")"

    print(f"{table_name} - saving...")
    conn = mariadb_connection(pool)
    cur = conn.cursor()

    create_table(cur, table_name, cols_table_request, keys)
    [request_table_insert_into(cur, table_name, cols_name, values_name, list(row.values))
     for index, row in data.iterrows()]

    conn.commit()
    conn.close()
    print(f"{table_name} - saved !")


if __name__ == '__main__':
    print(exists_table(None, "insee_communes"))
    print(exists_table(None, "table_unknown"))


