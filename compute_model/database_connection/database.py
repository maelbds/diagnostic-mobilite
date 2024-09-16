from compute_model.database_connection.db_connection_info import user, password, host, port, database
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


connection_url = URL.create(
    drivername="mariadb+mariadbconnector",
    username=user,
    password=password,
    host=host,
    port=port,
    database=database,
)

engine = create_engine(connection_url, pool_size=5, pool_recycle=3600)

