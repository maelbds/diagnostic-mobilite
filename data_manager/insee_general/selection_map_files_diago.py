import pandas as pd
from pyproj import Transformer

from data_manager.database_connection.sql_connect import mariadb_connection


def get_communes(pool, year):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT c.COM, c.LIBELLE, c.ARR, c.DEP, c.REG,
                            e.EPCI, aav.AAV, aav.CATEAAV,
                            ign.chflieu_lat, ign.chflieu_lon
                FROM insee_cog_communes AS c 
                JOIN insee_epci_communes AS e ON c.COM = e.CODGEO
                JOIN insee_aav_communes AS aav ON c.COM = aav.CODGEO
                JOIN ign_commune_center AS ign ON ign.geo_code = c.COM
                WHERE c.year_data = ? AND e.year_data = ? AND aav.year_cog = ?""",
                [year, year, year, year, "IGN_"+year])
    result = list(cur)
    conn.close()

    communes = pd.DataFrame(result, columns=["geo_code", "name", "arr", "dep", "reg",
                                             "epci", "aav", "cate_aav",
                                             "cheflieu_lat", "cheflieu_lon"])

    transformer = Transformer.from_crs("epsg:4326", "epsg:2154")
    coords_xy_2154 = [list(transformer.transform(lat, lon))
                  for lon, lat in zip(communes["cheflieu_lon"], communes["cheflieu_lat"])]
    communes[["cheflieu_x2154", "cheflieu_y2154"]] = coords_xy_2154

    communes.drop(columns=["cheflieu_lat", "cheflieu_lon"], inplace=True)

    return communes


def get_epci(pool, year):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT EPCI, LIBEPCI
                FROM insee_epci
                WHERE year_data = ?""",
                [year])
    result = list(cur)
    conn.close()

    epci = pd.DataFrame(result, columns=["epci", "epci_name"])
    return epci


def get_arrondissements(pool, year):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT ARR, CHEFLIEU, LIBELLE
                FROM insee_cog_arrondissements
                WHERE year_data = ?""",
                [year])
    result = list(cur)
    conn.close()

    arr = pd.DataFrame(result, columns=["arr", "arr_chef_lieu", "arr_name"])
    return arr


def get_departements(pool, year):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT DEP, CHEFLIEU, LIBELLE
                FROM insee_cog_departements
                WHERE year_data = ?""",
                [year])
    result = list(cur)
    conn.close()

    dep = pd.DataFrame(result, columns=["dep", "dep_chef_lieu", "dep_name"])
    return dep


def get_aav(pool, year):
    conn = mariadb_connection(pool)
    cur = conn.cursor()
    cur.execute("""SELECT a.AAV, a.LIBAAV, a.TAAV
                FROM insee_aav AS a
                WHERE a.year_cog = ? """,
                [year])
    result = list(cur)
    conn.close()

    aav = pd.DataFrame(result, columns=["aav", "aav_name", "aav_type"])
    return aav

# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 4000)


    epci = get_epci(None, "2022")
    epci.to_csv("epci_attr.csv", index=False)
    print(epci)

    arr = get_arrondissements(None, "2022")
    arr.to_csv("arrondissements_attr.csv", index=False)
    print(arr)

    dep = get_departements(None, "2022")
    dep.to_csv("departements_attr.csv", index=False)
    print(dep)

    aav = get_aav(None, "2022")
    aav.to_csv("aav_attr.csv", index=False)
    print(aav)

    communes = get_communes(None, "2022")
    communes = pd.merge(communes, aav[["aav", "aav_type"]], on="aav")
    communes["typo_aav"] = communes.apply(lambda row: str(row["cate_aav"])[:1] + str(row["aav_type"]), axis=1)
    communes.drop(columns="aav_type", inplace=True)
    communes.to_csv("communes_attr.csv", index=False)
    print(communes)
