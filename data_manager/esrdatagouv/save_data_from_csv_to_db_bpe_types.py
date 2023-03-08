import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection


def get_universities_types_from_csv():
    type_cols = ["Code type", "Type"]
    type = pd.read_csv(
        "data/2017/fr-esr-implantations_etablissements_d_enseignement_superieur_publics.csv",
        sep=";", dtype=str,
        usecols=type_cols)
    type = type.rename(columns={"Code type": "id_univ_type", "Type": "name_univ_type"})
    type = type.dropna()
    type["id_type"] = 58
    type["id_category"] = 1
    type = type.drop_duplicates()
    type = type.sort_values(by="id_univ_type")
    print(type)
    return type


def save_data_from_csv_to_db(data):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ")"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ")"

    def request(cur, cols):
        cur.execute("""INSERT INTO esrdatagouv_universities_types """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    univ_types = get_universities_types_from_csv()
    print(univ_types)
    # to prevent from unuseful loading data
    security = True
    if not security:
        save_data_from_csv_to_db(univ_types)
