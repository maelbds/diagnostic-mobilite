import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection


def get_universities_from_csv():
    cols = ["Code commune",
            "Implantation", "Code de l'implantation", "Géolocalisation", "Effectif d'étudiants inscrits",
            "Nature", "Code nature", "Type", "Code type",
            "Code de l'unité de rattachement", "Unité de rattachement",
            "type de l'établissement siège", "Code de l'établissement siège", "Etablissement siège"]
    data = pd.read_csv(
        "data/2017/fr-esr-implantations_etablissements_d_enseignement_superieur_publics.csv",
        sep=";", dtype=str,
        usecols=cols)

    mask_type = data["Code type"].isin(["UNIV", "ING", "FORP", "CFA", "CNED", "PBAC"])
    data = data.loc[mask_type]

    data = data.dropna(subset=["Géolocalisation"])
    data["lat"] = data["Géolocalisation"].apply(lambda x: x.split(", ")[0])
    data["lon"] = data["Géolocalisation"].apply(lambda x: x.split(", ")[1])
    data = data.drop(columns=["Géolocalisation"])

    data = data.rename(columns={"Code commune": "geo_code",
                                "Code de l'implantation": "id",
                                "Implantation": "name",
                                "Effectif d'étudiants inscrits": "student_nb",
                                "Nature": "nature",
                                "Code nature": "code_nature",
                                "Type": "type",
                                "Code type": "code_type",
                                "Code de l'unité de rattachement": "unit_id",
                                "Unité de rattachement": "unit_name",
                                "type de l'établissement siège": "etab_type",
                                "Code de l'établissement siège": "etab_id",
                                "Etablissement siège": "etab_name"})

    print(data)

    data["name"] = data["name"].apply(lambda x: x.lower().title() if type(x) is str else "")
    data["unit_name"] = data["unit_name"].apply(lambda x: x.lower().title() if type(x) is str else "")
    data["etab_name"] = data["etab_name"].apply(lambda x: x.lower().title() if type(x) is str else "")

    data = data.drop_duplicates(subset="id")
    return data


def save_data_from_csv_to_db(data):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ", source)"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ", 'ESR_GOUV_2017')"

    def request(cur, cols):
        cur.execute("""INSERT INTO esrdatagouv_universities """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    univ = get_universities_from_csv()
    univ = univ.replace({np.nan: None})
    print(univ)
    # to prevent from unuseful loading data
    security = True
    if not security:
        save_data_from_csv_to_db(univ)
