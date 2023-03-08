import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError

from data_manager.insee_local.source import SOURCE_POPULATION_STATUS


def get_pop_status_nb(pool, geo_code, source=SOURCE_POPULATION_STATUS):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT retired, 
                        employed, 
                        unemployed, 
                        other, 
                        scholars_2_5, 
                        scholars_6_10, 
                        scholars_11_14, 
                        scholars_15_17, 
                        scholars_18
                FROM insee_pop_status_nb 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        pop_status_nb = {
            "retired": result[0],
            "employed": result[1],
            "unemployed": result[2],
            "other": result[3],
            "scholars_2_5": result[4],
            "scholars_6_10": result[5],
            "scholars_11_14": result[6],
            "scholars_15_17": result[7],
            "scholars_18": result[8]
        }
        return pop_status_nb
    else:
        return None


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        print(get_pop_status_nb(None, 79048))
        print(get_pop_status_nb(None, 13041))

        total = {'retired': 0,
                 'employed': 0,
                 'unemployed': 0,
                 'other': 0,
                 'scholars_2_5': 0,
                 'scholars_6_10': 0,
                 'scholars_11_14': 0,
                 'scholars_15_17': 0,
                 'scholars_18': 0}

        cc_balcon_dauphine = ['38261', '38465', '38050', '38554', '38542', '38539', '38535', '38532', '38515', '38507',
                              '38488', '38467', '38451', '38415', '38392', '38374', '38294', '38282', '38260', '38250',
                              '38210', '38190', '38176', '38146', '38138', '38109', '38067', '38026', '38010', '38546',
                              '38543', '38525', '38494', '38483', '38458', '38365', '38320', '38297', '38295', '38247',
                              '38139', '38135', '38124', '38083', '38055', '38054', '38022']

        for g in ["79048", "79270"]:
            for key, value in get_pop_status_nb(None, g).items():
                total[key] += value

        total.pop("scholars_2_5", None)
        pprint.pprint(total)
        total = {k: v / sum(total.values()) * 100 for k, v in total.items()}
        pprint.pprint(total)

    except UnknownGeocodeError as e:
        print(e.message)
