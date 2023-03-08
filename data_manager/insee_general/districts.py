import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection


def district_to_city(geo_code):
    conn = mariadb_connection()
    cur = conn.cursor()
    cur.execute("""SELECT geo_code_city FROM insee_arrondissements 
                WHERE geo_code_district = ?""", [geo_code])
    result = list(cur)
    conn.close()
    return result[0][0] if len(result)> 0 else geo_code


def city_to_districts(pool, geo_code):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT geo_code_district FROM insee_arrondissements 
                WHERE geo_code_city = ?""", [geo_code])
    result = list(cur)
    conn.close()
    return [r[0] for r in result] if len(result)> 0 else [geo_code]


def get_districts(pool):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT geo_code_district, geo_code_city FROM insee_arrondissements""", [])
    result = list(cur)
    districts = pd.DataFrame(result, columns=["district", "city"])
    conn.close()
    return districts


def list_district_to_city(pool, list_districts):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM insee_arrondissements""", [])
    result = list(cur)
    conn.close()
    district_dict = pd.DataFrame(result, columns=["geo_code_district", "geo_code_commune"])
    list_districts = pd.Series(list_districts, name="geo_code_district")
    list_city = pd.merge(list_districts, district_dict, on="geo_code_district", how="left")
    list_city["geo_code_commune"] = list_city["geo_code_commune"].fillna(list_city["geo_code_district"])
    return list_city["geo_code_commune"]


def geo_codes_city_to_district(pool, geo_codes):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM insee_arrondissements""", [])
    result = list(cur)
    conn.close()
    district_dict = pd.DataFrame(result, columns=["geo_code_district", "geo_code_commune"])
    geo_codes = pd.DataFrame(geo_codes, columns=["geo_code"])
    geo_codes = pd.merge(geo_codes, district_dict, left_on="geo_code", right_on="geo_code_commune", how="outer").\
        dropna(subset=["geo_code"])
    geo_codes["geo_code_district"] = geo_codes["geo_code_district"].fillna(geo_codes["geo_code"])
    return geo_codes["geo_code_district"].to_list()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    #print(district_to_city("69387"))
    montpellier_district = ['04034', '04063', '04081', '04094', '04112', '04138', '04143', '04152', '04188', '04189', '04197', '04230', '04242', '04245', '13001', '13002', '13003', '13004', '13005', '13006', '13007', '13008', '13009', '13010', '13011', '13012', '13013', '13014', '13015', '13016', '13017', '13018', '13019', '13020', '13021', '13022', '13023', '13024', '13025', '13026', '13027', '13028', '13029', '13030', '13031', '13032', '13033', '13034', '13035', '13036', '13037', '13038', '13039', '13040', '13041', '13042', '13043', '13044', '13045', '13046', '13047', '13048', '13049', '13050', '13051', '13052', '13053', '13054', '13056', '13057', '13058', '13059', '13060', '13061', '13062', '13063', '13064', '13065', '13066', '13067', '13068', '13069', '13070', '13071', '13072', '13073', '13074', '13075', '13076', '13077', '13078', '13079', '13080', '13081', '13082', '13083', '13084', '13085', '13086', '13087', '13088', '13089', '13090', '13091', '13092', '13093', '13094', '13095', '13096', '13097', '13098', '13099', '13100', '13101', '13102', '13103', '13104', '13105', '13106', '13107', '13108', '13109', '13110', '13111', '13112', '13113', '13114', '13115', '13116', '13117', '13118', '13119', '13201', '13202', '13203', '13204', '13205', '13206', '13207', '13208', '13209', '13210', '13211', '13212', '13213', '13214', '13215', '13216', '30032', '30117', '34005', '34010', '34011', '34012', '34013', '34014', '34016', '34022', '34023', '34024', '34027', '34029', '34033', '34035', '34036', '34039', '34041', '34042', '34043', '34045', '34047', '34048', '34050', '34051', '34057', '34058', '34060', '34064', '34066', '34067', '34076', '34077', '34078', '34079', '34082', '34087', '34088', '34090', '34095', '34102', '34103', '34106', '34108', '34110', '34111', '34113', '34114', '34115', '34116', '34118', '34120', '34122', '34123', '34124', '34125', '34127', '34128', '34129', '34131', '34133', '34134', '34137', '34138', '34142', '34143', '34145', '34146', '34150', '34151', '34152', '34153', '34154', '34156', '34157', '34159', '34163', '34164', '34165', '34169', '34171', '34172', '34173', '34174', '34176', '34177', '34179', '34180', '34185', '34188', '34192', '34194', '34195', '34197', '34198', '34202', '34204', '34205', '34208', '34210', '34212', '34213', '34215', '34217', '34220', '34221', '34222', '34227', '34233', '34239', '34240', '34241', '34242', '34243', '34244', '34246', '34247', '34248', '34249', '34251', '34254', '34255', '34256', '34259', '34261', '34262', '34263', '34264', '34265', '34266', '34267', '34268', '34270', '34272', '34274', '34276', '34277', '34280', '34281', '34282', '34283', '34286', '34287', '34288', '34290', '34292', '34294', '34295', '34296', '34297', '34301', '34303', '34304', '34306', '34307', '34309', '34313', '34314', '34316', '34317', '34318', '34320', '34321', '34322', '34323', '34327', '34328', '34333', '34337', '34340', '34341', '34342', '34343', '34344', '83006', '83021', '83025', '83052', '83066', '83087', '83089', '83093', '83096', '83097', '83104', '83110', '83113', '83114', '83116', '83120', '83125', '83135', '83140', '83145', '83146', '83150', '84002', '84009', '84010', '84014', '84024', '84026', '84042', '84052', '84065', '84068', '84074', '84076', '84084', '84089', '84090', '84093', '84095', '84113', '84121', '84133', '84140', '84147', '84151']

    print(city_to_districts(None, 13055))
    print(city_to_districts(None, 79048))
