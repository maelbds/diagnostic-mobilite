import pandas as pd
import numpy as np

from data_manager.database_connection.sql_connect import mariadb_connection

import shapefile
from shapely.geometry import shape, Point


def read_shp_communes():
    sf = shapefile.Reader(
        "C:/Users/maelb/Documents/6 - Mobilite/1 - Produit/diagnostic-mobilite/data_manager/ign/data/ADMIN-EXPRESS-COG-CARTO_3-1__SHP__FRA_WM_2022-04-15/ADMIN-EXPRESS-COG-CARTO/1_DONNEES_LIVRAISON_2022-04-15\ADECOGC_3-1_SHP_WGS84G_FRA/COMMUNE")

    communes_geo = [r.__geo_interface__ for r in sf.shapeRecords()]
    communes = pd.DataFrame([{"id_com": c["properties"]["ID"],
                              "geo_code": c["properties"]["INSEE_COM"],
                              "shape": shape(c["geometry"])}
                             for c in communes_geo])
    print(communes)
    return communes


def get_irve_from_csv():
    # https://schema.data.gouv.fr/etalab/schema-irve-statique/latest/documentation.html
    cols = ["code_insee_commune",
            "id_station_itinerance", "nom_station", "implantation_station", "coordonneesXY",
            "nom_operateur", "nom_amenageur",
            "nbre_pdc", "id_pdc_itinerance", "puissance_nominale", "prise_type_ef", "prise_type_2",
            "prise_type_combo_ccs", "prise_type_chademo", "prise_type_autre",
            "condition_acces",
            "date_maj"]
    data = pd.read_csv(
        "data/irve/IRVE_20230220.csv",
        sep=",", dtype=str,
        usecols=cols)

    data["lat"] = [float(coords.replace(" ", "")[1:-1].split(",")[1]) for coords in data["coordonneesXY"]]
    data["lon"] = [float(coords.replace(" ", "")[1:-1].split(",")[0]) for coords in data["coordonneesXY"]]
    data = data.drop(columns=["coordonneesXY"])
    print(data)
    print(data[data["code_insee_commune"].isna()])

    mask_no_geocode = data["code_insee_commune"].isna()

    communes_shapes = read_shp_communes()
    def find_geocode(row):
        lat = row["lat"]
        lon = row["lon"]
        point = Point(lon, lat)
        mask_is_in = [s.contains(point) for s in communes_shapes["shape"]]
        if sum(mask_is_in) > 0:
            return communes_shapes.loc[mask_is_in, "geo_code"].iloc[0]
        else:
            return None

    data.loc[mask_no_geocode, "code_insee_commune"] = data.loc[mask_no_geocode, ["lat", "lon"]].apply(find_geocode, axis=1)

    print(data[mask_no_geocode])

    print(data)
    print(data[data["code_insee_commune"].isna()])
    return data


def save_data_from_csv_to_db(data):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ", source)"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ", 'IRVE_20230220')"

    def request(cur, cols):
        cur.execute("""INSERT INTO transportdatagouv_irve """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)

    irve = get_irve_from_csv()

    # to prevent from unuseful loading data
    security = True
    if not security:
        irve = irve.replace({np.nan: None})
        print(irve)
        #save_data_from_csv_to_db(irve)
