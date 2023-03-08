# Module Imports
import mariadb
import sys

from data_manager.database_connection.db_connection_info import user, password, host, port, database


def mariadb_connection(pool=None):
    # Connect to MariaDB Platform
    conn = False
    try:
        if pool is None:
            conn = mariadb.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=database
            )
            print("no pool")
        else:
            conn = pool.get_connection()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    return conn


def mariadb_connection_pool():
    # Connect to MariaDB Platform
    conn = False
    conn_params = {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "database": database
    }

    try:
        # create new pool
        pool = mariadb.ConnectionPool(pool_name="web-app", pool_size=20, **conn_params)
        # get a connection from pool

    except mariadb.Error as e:
        print(f"Error creating MariaDB pool: {e}")
        sys.exit(1)

    return pool


