import pprint
import pandas as pd
from pyproj import Transformer

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError
from data_manager.insee_filosofi.source import SOURCE_GRIDDED_POP


def get_gridded_population(pool, geo_code, source=SOURCE_GRIDDED_POP):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT idGrid200, Ind, Men, Men_pauv, Men_prop, Ind_snv, Men_surf
                FROM insee_filosofi_gridded_pop 
                WHERE geo_code = ? AND source = ?""", [geo_code, source])

    result = list(cur)
    gridded_population = pd.DataFrame(result, columns=["idGrid200", "population", "households", "poor_households",
                                                       "owner_households", "sum_incomes", "sum_hh_surface"], dtype=str)
    conn.close()

    # Lambert to Geodetic coordinates system :
    transformer = Transformer.from_crs("epsg:3035",  # Système Inspire
                                       "epsg:4326")  # World Geodetic System (lat/lon)

    def lambert_to_geo(x, y):
        lat, lon = transformer.transform(x, y)
        return [lat, lon]

    def idToCoords(id):
        coords = id.split("N")[-1]
        x, y = coords.split("E")
        return lambert_to_geo(x, y)

    gridded_population["coords"] = gridded_population["idGrid200"].apply(lambda id: idToCoords(id))
    gridded_population = gridded_population.astype({"population": "float",
                                                    "households": "float",
                                                    "poor_households": "float",
                                                    "owner_households": "float",
                                                    "sum_incomes": "float",
                                                    "sum_hh_surface": "float"})

    gridded_population.drop(columns="idGrid200", inplace=True)

    return gridded_population.to_dict(orient="records")


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pprint.pprint(get_gridded_population(None, "79048"))
    except UnknownGeocodeError as e:
        print(e.message)
