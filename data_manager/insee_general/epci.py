import pandas as pd
from shapely import wkb
import json

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.exception import UnknownGeocodeError

from data_manager.insee_general.source import SOURCE_EPCI


def get_geo_codes_from_epci_name(name, source=SOURCE_EPCI):
    conn = mariadb_connection()
    cur = conn.cursor()
    cur.execute("""SELECT geo_code FROM insee_communes_epci
                JOIN insee_epci
                ON insee_communes_epci.epci_siren = insee_epci.epci_siren
                WHERE insee_epci.epci_name = ? AND insee_epci.source = ? AND insee_communes_epci.source = ?""",
                [name, source, source])
    result = list(cur)
    epci = pd.DataFrame(result, columns=["geo_code"], dtype=str)
    conn.close()
    return epci["geo_code"].to_list()


def get_all_epci(source=SOURCE_EPCI):
    conn = mariadb_connection()
    cur = conn.cursor()
    cur.execute("""SELECT insee_epci.epci_siren, epci_name, outline_light  
                FROM insee_epci
                JOIN ign_epci_outline ON insee_epci.epci_siren = ign_epci_outline.epci_siren
                WHERE insee_epci.source = ?
                """, [source])
    result = list(cur)
    epci = pd.DataFrame(result, columns=["epci_siren", "epci_name", "outline_light"])
    conn.close()

    def wkb_to_geojson(wkb_geom):
        geom_collection = wkb.loads(wkb_geom)
        geom = geom_collection[0].__geo_interface__
        return geom

    epci["outline_light"] = epci["outline_light"].apply(lambda outline: wkb_to_geojson(outline))

    epci = epci.to_dict(orient="records")
    return epci


def get_epci(pool, geo_code, source=SOURCE_EPCI):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT epci_siren FROM insee_communes_epci
                WHERE geo_code = ? AND source = ?""",
                [geo_code, source])
    result = list(cur)
    conn.close()

    if len(result) > 0:
        result = result[0]
        epci_code = result[0]
        return epci_code
    else:
        raise UnknownGeocodeError(geo_code)


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    print(get_geo_codes_from_epci_name("CC Haut Val de Sèvre"))
    epci = get_all_epci()
    print(epci)

    print(get_epci(None, "79048"))

    with open('epci.json', 'w') as fp:
        json.dump(epci, fp)


