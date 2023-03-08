import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection


def get_population_status_from_csv():
    variables = pd.read_csv("data/2018/dossier_complet/variables_population_status.csv", sep=";", dtype=str)
    cols = variables["variables"].dropna().tolist()
    print(cols)

    data = pd.read_csv(
        "data/2018/dossier_complet/dossier_complet.csv",
        sep=";", dtype=str,
        usecols=cols)
    data = data.rename(columns={"CODGEO": "geo_code"})
    data.loc[:, data.columns != 'geo_code'] = data.loc[:, data.columns != 'geo_code'].astype("float").round()
    print(data[data["geo_code"]=="79048"])
    population_status = data.rename(columns={
        "C18_POP15P_CS7": "retired",
        "P18_SCOL0205": "scholars_2_5",
        "P18_SCOL0610": "scholars_6_10",
        "P18_SCOL1114": "scholars_11_14",
        "P18_SCOL1517": "scholars_15_17",
        "P18_ACTOCC15P": "employed",
        "P18_CHOM1564": "unemployed"
    })
    population_status["scholars_18"] = population_status["P18_SCOL1824"] + \
                                       population_status["P18_SCOL2529"] + \
                                       population_status["P18_SCOL30P"]
    population_status.drop(columns=["P18_SCOL1824", "P18_SCOL2529", "P18_SCOL30P"], inplace=True)
    print(population_status)

    population_status["other"] = population_status["P18_POP"] \
                                 - population_status["P18_POP0014"] \
                                 - population_status["retired"] \
                                 - population_status["employed"] \
                                 - population_status["unemployed"] \
                                 - population_status["scholars_15_17"] \
                                 - population_status["scholars_18"]
    population_status["other"] = population_status["other"].apply(lambda x: max(0, x))
    population_status = population_status.drop(columns=["P18_POP0014"])
    print(population_status)

    return population_status


def save_data_from_csv_to_db(data):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ", date, source)"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ", CURRENT_TIMESTAMP, 'INSEE_RP_2018')"

    def request(cur, cols):
        cur.execute("""INSERT INTO insee_pop_status_nb """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    pop_status = get_population_status_from_csv()

    cc_val_dauphine = ['38509', '38377', '38315', '38001', '38398', '38381', '38343', '38076', '38401', '38341', '38064', '38560', '38520', '38508', '38464', '38434', '38420', '38369', '38357', '38354', '38323', '38296', '38257', '38246', '38183', '38162', '38148', '38147', '38104', '38098', '38089', '38047', '38044', '38038', '38029', '38012']
    cc_lyon_st_exupery = ["38011", "38085", "38097", "38197", "38316", "38507", "38557"]
    cc_balcon_dauphine = ['38261', '38465', '38050', '38554', '38542', '38539', '38535', '38532', '38515', '38507', '38488', '38467', '38451', '38415', '38392', '38374', '38294', '38282', '38260', '38250', '38210', '38190', '38176', '38146', '38138', '38109', '38067', '38026', '38010', '38546', '38543', '38525', '38494', '38483', '38458', '38365', '38320', '38297', '38295', '38247', '38139', '38135', '38124', '38083', '38055', '38054', '38022']

    marseille_pertuis = ["84089", "13059", "13074", "13048", "13099"]
    marseille_gardanne = ["13015", "13041", "13107"]
    marseille_pertuis_luberon = ['84147', '84133', '84113', '84084', '84076', '84026', '84024', '84014', '84010', '84002', '84151', '84121', '84090', '84052', '84042', '84009', '84089', '84074', '84093', '84065', '84095', '84068', '84140']
    marseille_baux_provence = ['13076', '13116', '13083', '13066', '13052', '13045', '13036', '13027', '13018', '13010', '13089', '13067', '13064', '13100', '13094', '13057', '13068', '13038', '13065', '13058', '13034', '13011', '13006']

    for geo_codes in [marseille_baux_provence]:
        mask_territory = pop_status["geo_code"].isin(geo_codes)
        print(pop_status[mask_territory].sum())

    # to prevent from unuseful loading data
    security = True
    if not security:
        pop_status = pop_status.replace({np.nan: None})
        print(pop_status)
        print(pop_status[pop_status["geo_code"] == "79048"])
        print(pop_status[pop_status["geo_code"] == "79128"])
        save_data_from_csv_to_db(pop_status)
