from data_manager.db_functions import create_new_table


def create_table_stats_api(pool):
    table_name = "stats_api"
    cols_table = {
        "id": "INT NOT NULL AUTO_INCREMENT",
        "session_id": "VARCHAR(50) NULL DEFAULT NULL",
        "ip": "VARCHAR(15) NULL DEFAULT NULL",
        "name": "VARCHAR(50) NULL DEFAULT NULL",
        "geo_codes": "TEXT NULL DEFAULT NULL",
        "mesh": "VARCHAR(20) NULL DEFAULT NULL",
        "year": "VARCHAR(20) NULL DEFAULT NULL",
        "datetime": "DATETIME NULL DEFAULT NULL"
    }
    keys = "PRIMARY KEY (id) USING BTREE, KEY (session_id) USING BTREE"

    create_new_table(pool, table_name, cols_table, keys)


if __name__ == '__main__':
    create_table_stats_api(None)