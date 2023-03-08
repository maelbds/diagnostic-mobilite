import pprint
import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError
from data_manager.insee_local.source import SOURCE_POPULATION


def get_csp(pool, geo_code, source=SOURCE_POPULATION):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT C18_POP15P, C18_POP15P_CS1, C18_POP15P_CS2, C18_POP15P_CS3, 
                C18_POP15P_CS4, C18_POP15P_CS5, C18_POP15P_CS6, C18_POP15P_CS7, C18_POP15P_CS8
                FROM insee_population 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        csp = {
            "total15+": {
                "label": "Population de plus de 15 ans",
                "value": result[0]
            },
            "csp1": {
                "label": "Agriculteurs exploitants",
                "value": result[1]
            },
            "csp2": {
                "label": "Artisans, Commerçants, Chefs d'entreprise",
                "value": result[2]
            },
            "csp3": {
                "label": "Cadres, Professions intellectuelles supérieures",
                "value": result[3]
            },
            "csp4": {
                "label": "Professions intermédiaires",
                "value": result[4]
            },
            "csp5": {
                "label": "Employés",
                "value": result[5]
            },
            "csp6": {
                "label": "Ouvriers",
                "value": result[6]
            },
            "csp7": {
                "label": "Retraités",
                "value": result[7]
            },
            "csp8": {
                "label": "Autres",
                "value": result[8]
            },
        }
        return csp
    else:
        return None


def get_csp_marginals(pool, geo_code, source=SOURCE_POPULATION):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT C18_POP15P, C18_POP15P_CS1, C18_POP15P_CS2, C18_POP15P_CS3, 
                C18_POP15P_CS4, C18_POP15P_CS5, C18_POP15P_CS6, C18_POP15P_CS7, C18_POP15P_CS8
                FROM insee_population 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        csp = {
            "1": result[1],
            "2": result[2],
            "3": result[3],
            "4": result[4],
            "5": result[5],
            "6": result[6]
        }
        return csp
    else:
        return None


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_csp(None, 79048))
        pprint.pprint(get_csp_marginals(None, 79048))

        ca_terres_de_provence = ['13076', '13116', '13083', '13066', '13052', '13045', '13036', '13027', '13018',
                                 '13010', '13089', '13067', '13064']
        cc_val_dauphine = ['38509', '38377', '38315', '38001', '38398', '38381', '38343', '38076', '38401', '38341',
                           '38064', '38560', '38520', '38508', '38464', '38434', '38420', '38369', '38357', '38354',
                           '38323', '38296', '38257', '38246', '38183', '38162', '38148', '38147', '38104', '38098',
                           '38089', '38047', '38044', '38038', '38029', '38012']
        cc_beaujolais_pierre_doree = ['69246', '69245', '69239', '69230', '69212', '69159', '69156', '69140', '69134',
                                      '69126', '69125', '69122', '69121', '69113', '69111', '69106', '69090', '69059',
                                      '69056', '69055', '69052', '69050', '69049', '69047', '69039', '69026', '69024',
                                      '69020', '69017', '69009', '69005', '69004']

        csp = {
                "csp1": 0,
                "csp2": 0,
                "csp3": 0,
                "csp4": 0,
                "csp5": 0,
                "csp6": 0,
                "csp7": 0,
                "csp8": 0,
                "total15+": 0,
            }
        for g in cc_beaujolais_pierre_doree:
            csp_g = get_csp(None, g)
            for key, value in csp_g.items():
                csp[key] += value["value"]

        print(csp)
        csp = {key: round(value/csp["total15+"]*100, 1) for key, value in csp.items()}
        print(csp)


    except UnknownGeocodeError as e:
        print(e.message)
