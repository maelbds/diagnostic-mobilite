# Module Imports

import mariadb
import sys
import pandas as pd


from data_manager.database_connection.db_connection_info import user, password, host, port, database
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import scoped_session, sessionmaker


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
            try:
                conn = pool.get_connection()

            except mariadb.PoolError as e:
                # Report Error
                print(f"Error opening connection from pool: {e}")

                # Create New Connection as Alternate
                conn = mariadb.connect(
                    user=user,
                    password=password,
                    host=host,
                    port=port,
                    database=database
                )
                print("New connection created as alternate")

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
        print("Created pool size of '%s': %s" % (pool.pool_name, pool.pool_size))

    except mariadb.Error as e:
        print(f"Error creating MariaDB pool: {e}")
        sys.exit(1)

    return pool


def db_engine():
    connection_url = URL.create(
        drivername="mariadb+mariadbconnector",
        username=user,
        password=password,
        host=host,
        database=database,
    )
    engine = create_engine(connection_url, pool_size=5, pool_recycle=3600)

    """with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM insee_communes LIMIT 10"))
        result = pd.DataFrame(result.all())
        print(result)

        test = pd.read_sql("SELECT * FROM insee_communes LIMIT 10", engine)
        print(test)

        conn.close()"""

    Session = scoped_session(sessionmaker(bind=engine, autocommit=False))

    for i in range(100):
        print(i)
        with Session.connection() as conn:
            print(conn)
            result = conn.execute(text("SELECT * FROM insee_communes LIMIT 10"))
            result = pd.DataFrame(result.all())
            print(result)
            result = conn.execute(text("SELECT * FROM insee_communes LIMIT 100"))
            result = pd.DataFrame(result.all())
            print(result)


if __name__ == '__main__':
    db_engine()
