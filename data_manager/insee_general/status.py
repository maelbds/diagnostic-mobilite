import pprint
import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError, UnknownPostalcodeError
from data_manager.insee_local.population import get_population


def get_uu_status(pool, geo_code):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT status_code
                FROM insee_communes_status 
                WHERE geo_code = ?""", [geo_code])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        status = result[0]

        return status
    else:
        raise UnknownGeocodeError(geo_code)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_uu_status(None, "79048"))
        pprint.pprint(get_uu_status(None, "79191"))
        pprint.pprint(get_uu_status(None, "79270"))

        cc_val_dauphine = ['38509', '38377', '38315', '38001', '38398', '38381', '38343', '38076', '38401', '38341',
                           '38064', '38560', '38520', '38508', '38464', '38434', '38420', '38369', '38357', '38354',
                           '38323', '38296', '38257', '38246', '38183', '38162', '38148', '38147', '38104', '38098',
                           '38089', '38047', '38044', '38038', '38029', '38012']
        cc_lyon_st_exupery = ["38011", "38085", "38097", "38197", "38316", "38507", "38557"]
        cc_balcon_dauphine = ['38261', '38465', '38050', '38554', '38542', '38539', '38535', '38532', '38515', '38507',
                              '38488', '38467', '38451', '38415', '38392', '38374', '38294', '38282', '38260', '38250',
                              '38210', '38190', '38176', '38146', '38138', '38109', '38067', '38026', '38010', '38546',
                              '38543', '38525', '38494', '38483', '38458', '38365', '38320', '38297', '38295', '38247',
                              '38139', '38135', '38124', '38083', '38055', '38054', '38022']

        marseille_pertuis = ["84089", "13059", "13074", "13048", "13099"]
        marseille_gardanne = ["13015", "13041", "13107"]
        marseille_pertuis_luberon = ['84147', '84133', '84113', '84084', '84076', '84026', '84024', '84014', '84010',
                                     '84002', '84151', '84121', '84090', '84052', '84042', '84009', '84089', '84074',
                                     '84093', '84065', '84095', '84068', '84140']


        for geo_codes in [marseille_pertuis_luberon, marseille_gardanne, cc_balcon_dauphine, cc_val_dauphine]:
            result = pd.DataFrame()
            status = [get_uu_status(None, g) for g in geo_codes]
            pop = [get_population(None, g) for g in geo_codes]
            result = pd.DataFrame({"status": status, "pop": pop})
            print("---")
            print(result.groupby("status").sum())

    except UnknownGeocodeError as e:
        print(e.message)
