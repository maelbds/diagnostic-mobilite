import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.entd.source import SOURCE_ENTD


def get_entd_reasons(source=SOURCE_ENTD):
    conn = mariadb_connection()
    cur = conn.cursor()
    if source == "2018":
        cur.execute("""SELECT * FROM entd_reasons_2018""")
    elif source == "2008":
        cur.execute("""SELECT * FROM entd_reasons_2008""")
    result = list(cur)
    reasons = pd.DataFrame(result, columns=["id_entd", "id_reason"], dtype=int)
    conn.close()
    return reasons


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    ENTD_CATEGORIES = get_entd_reasons("2018")
    print(ENTD_CATEGORIES)
