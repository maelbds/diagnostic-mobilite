import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection


def get_population_from_csv():
    variables = pd.read_csv("data/2018/pop2018/variables.csv", sep=";", dtype=str)
    print(variables)
    cols = variables["pop2018"].dropna().tolist()
    print(cols)

    data = pd.read_csv(
        "data/2018/pop2018/base-ic-evol-struct-pop-2018.csv",
        sep=";", dtype=str,
        usecols=cols)
    data = data.rename(columns={"COM": "geo_code"})
    data.loc[:, data.columns != 'geo_code'] = data.loc[:, data.columns != 'geo_code'].astype("float").round()
    return data


def save_population_from_csv_to_db(pop):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in pop.columns]) + ", date, source)"
    values_name = "(" + ", ".join(["?" for col in pop.columns]) + ", CURRENT_TIMESTAMP, 'INSEE_POP_2018')"

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_pop_age """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in pop.iterrows()]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    population = get_population_from_csv()
    population = population.groupby("geo_code", as_index=False).sum()
    population = population.replace({np.nan: None})
    print(population)
    print(population[population["geo_code"] == "01004"])
    print(population[population["geo_code"] == "75056"])
    print(population[population["geo_code"] == "79048"])

    # to prevent from unuseful loading data
    security = True
    if not security:
        save_population_from_csv_to_db(population)
