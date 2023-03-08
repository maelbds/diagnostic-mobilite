import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection

from data_manager.entd.source import SOURCE_ENTD


def get_reasons(pool):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM reasons""")
    result = list(cur)
    reasons = pd.DataFrame(result, columns=["id", "name", "name_fr", "rank_main_activity"])
    conn.close()
    return reasons


def get_reasons_entd(pool, source_entd=SOURCE_ENTD):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    if source_entd == "2008":
        cur.execute("""
        SELECT entd_reasons_2008.id_entd, entd_reasons_2008.id_reason, reasons.name, reasons.name_fr
                FROM entd_reasons_2008 
                JOIN reasons 
                ON entd_reasons_2008.id_reason = reasons.id
        """)
    elif source_entd == "2018":
        cur.execute("""
        SELECT entd_reasons_2018.id_entd, entd_reasons_2018.id_reason, reasons.name, reasons.name_fr
                FROM entd_reasons_2018 
                JOIN reasons 
                ON entd_reasons_2018.id_reason = reasons.id
        """)
    result = list(cur)
    reasons_entd = pd.DataFrame(result, columns=["id_entd", "id_reason", "name", "name_fr"]).set_index("id_entd")
    conn.close()
    return reasons_entd


def categories_to_reasons(pool):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""
    SELECT  categories.name, reasons.name, reasons.name_fr
            FROM categories 
            JOIN reasons 
            ON categories.id_reason = reasons.id
    """)
    result = list(cur)
    category_to_reason = pd.DataFrame(result, columns=["category", "reason", "reason_fr"]).set_index("category")
    conn.close()
    return category_to_reason

# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    reasons = get_reasons(None)
    print(reasons)
    print(get_reasons_entd(None))
    print(categories_to_reasons(None))
