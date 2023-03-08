import pprint
import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError

from data_manager.geodip.source import SOURCE_PRECARIOUSNESS


def get_precariousness_prop(pool, geo_code, source=SOURCE_PRECARIOUSNESS):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT fuel_prop, 
                          fuel_housing_prop,
                          fuel_nb,
                          fuel_housing_nb
                FROM geodip_precariousness 
                LEFT JOIN insee_arrondissements ON geodip_precariousness.geo_code = insee_arrondissements.geo_code_district
                WHERE (geo_code = ? OR geo_code_city = ?) AND source = ?""", [geo_code, geo_code, source])
    result = list(cur)
    conn.close()

    precariousness = pd.DataFrame(result, columns=["fuel_prop", "fuel_housing_prop", "fuel_nb", "fuel_housing_nb"])
    precariousness["households"] = precariousness["fuel_nb"] / precariousness["fuel_prop"] * 100

    if precariousness["households"].sum() > 0:
        fuel_prop = round(precariousness["fuel_nb"].sum() / precariousness["households"].sum() * 100, 1)
        fuel_housing_prop = round(precariousness["fuel_housing_nb"].sum() / precariousness["households"].sum() * 100, 1)
        return {"fuel": fuel_prop,
                "fuel_housing": fuel_housing_prop}
    else:
        return None


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_precariousness_prop(None, 79048))
    except UnknownGeocodeError as e:
        print(e.message)
