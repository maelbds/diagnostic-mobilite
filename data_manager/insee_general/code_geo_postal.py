import pprint

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError, UnknownPostalcodeError


def geo_code_to_postal_code(pool, geo_code):
    """
    Convert INSEE geo code to postal code
    :param geo_code: (String) INSEE geo code
    :return: (String) Postal code
    """
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT postal_code 
                FROM insee_communes 
                WHERE geo_code = ?""", [geo_code])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        postal_code = result[0]
        return postal_code
    else:
        raise UnknownGeocodeError(geo_code)


def geo_code_to_name(pool, geo_code):
    """
    Convert INSEE geo code to name of the commune
    :param geo_code: (String) INSEE geo code
    :return: (String) Commune's name
    """
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT LIBELLE 
                FROM insee_cog_communes 
                WHERE COM = ?""", [geo_code])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        name = result[0]
        return name
    else:
        raise UnknownGeocodeError(geo_code)


def convert_name(name):
    """
    Function to convert name to fit insee standards : saint is st, "'" is " ", etc...
    :param name: (String)
    :return: (String) converted name
    """
    name = name.upper()
    name = name.replace('-', ' ').replace('\'', ' ')
    name = name.replace('SAINT', 'ST')
    return name


def postal_code_to_geo_code(pool, postal_code, name):
    """
    Convert postal code & associated name to INSEE geo_code of the commune
    :param postal_code: (String) postal code
    :param name: (String) commune's name
    :return: (String) INSEE geo_code of the commune
    """
    name = convert_name(name)
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT geo_code 
                FROM insee_communes 
                WHERE postal_code = ? AND name = ?""", [postal_code, name])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        geo_code = result[0]
        return geo_code
    else:
        raise UnknownPostalcodeError([postal_code, name])


def name_to_geo_code(pool, name, department_codes):
    """
    Convert postal code & associated name to INSEE geo_code of the commune
    :param postal_code: (String) postal code
    :param name: (String) commune's name
    :return: (String) INSEE geo_code of the commune
    """
    name = convert_name(name)
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT geo_code 
                FROM insee_communes 
                WHERE name = ?""", [name])
    result = list(cur)
    print(result)
    conn.close()

    if len(result) > 0:
        possible_codes = []
        for r in result:
            code = r[0]
            if code[0:2] in department_codes:
                possible_codes.append(code)
        if len(possible_codes) == 1:
            return possible_codes[0]
        else:
            print(result)
            print(name)
            geo_code = input()
            return geo_code
    else:
        print(f"Geocode for {name} ?")
        geo_code = input()
        return geo_code


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        print(name_to_geo_code(None, "MONTPELLIER", ["34", "11", "30", "13"]))
        pprint.pprint(geo_code_to_postal_code(None, 79048))
        pprint.pprint(geo_code_to_name(None, 13055))
    except UnknownGeocodeError as e:
        print(e.message)
    try:
        pprint.pprint(postal_code_to_geo_code(None, 79400, "saint maixent l'école"))
    except UnknownPostalcodeError as e:
        print(e.message)


