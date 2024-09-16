import os

user = os.getenv("DB_USER") if os.getenv("DB_USER") is not None else "root"
password = os.getenv("DB_PASSWORD") if os.getenv("DB_PASSWORD") is not None else "tabl0mob1dur@"
host = os.getenv("DB_HOST") if os.getenv("DB_HOST") is not None else "127.0.0.1"
port = 3306
database = os.getenv("DB_DATABASE") if os.getenv("DB_DATABASE") is not None else "mobility_raw_data"
