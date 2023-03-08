"""
To load data from csv to database | EXECUTE ONCE TO FILL DATABASE
"""
import pandas as pd
import polyline
import shapefile
import topojson as tp

from shapely.geometry import shape

from data_manager.database_connection.sql_connect import mariadb_connection


def read_shp_outlines():
    sf = shapefile.Reader(
        "data/ADMIN-EXPRESS-COG-CARTO_3-1__SHP__FRA_WM_2022-04-15\ADMIN-EXPRESS-COG-CARTO/1_DONNEES_LIVRAISON_2022-04-15\ADECOGC_3-1_SHP_WGS84G_FRA/COMMUNE")

    communes_geo = [r.__geo_interface__ for r in sf.shapeRecords()]
    communes_outlines = pd.DataFrame([{"geo_code": c["properties"]["INSEE_COM"],
                                       "outline": [c["geometry"]["coordinates"]]} if c["geometry"][
                                                                                         "type"] == "Polygon" else
                                      {"geo_code": c["properties"]["INSEE_COM"],
                                       "outline": c["geometry"]["coordinates"]}
                                      for c in communes_geo])
    print(communes_outlines)
    print(communes_outlines[communes_outlines["geo_code"] == "79048"])

    return communes_outlines


def read_shp_outlines_to_shapely():
    sf = shapefile.Reader(
        "C:/Users/maelb/Documents/6 - Mobilite/1 - Produit/diagnostic-mobilite/data_manager/ign/data/ADMIN-EXPRESS-COG-CARTO_3-1__SHP__FRA_WM_2022-04-15\ADMIN-EXPRESS-COG-CARTO/1_DONNEES_LIVRAISON_2022-04-15\ADECOGC_3-1_SHP_WGS84G_FRA/COMMUNE")

    communes_geo = [r.__geo_interface__ for r in sf.shapeRecords()]
    communes_outlines = pd.DataFrame([{"geo_code": c["properties"]["INSEE_COM"],
                                       "outline": shape(c["geometry"])}
                                      for c in communes_geo])
    return communes_outlines


def save_outlines_to_db(outlines):
    conn = mariadb_connection()
    cur = conn.cursor()

    def request(cur, cols):
        cur.execute("""INSERT INTO ign_commune_outline 
                        (geo_code,
                        outline, 
                        source) VALUES (?,?,?)""", cols)

    [request(cur, [geo_code, " ".join([polyline.encode(o[0], geojson=True) for o in outline]), "IGN_2022"]) for
     geo_code, outline in
     zip(outlines["geo_code"], outlines["outline"])]

    conn.commit()
    conn.close()
    print("done")
    return


def shp_to_light_geojson():
    sf = shapefile.Reader(
        "data/ADMIN-EXPRESS-COG-CARTO_3-1__SHP__FRA_WM_2022-04-15\ADMIN-EXPRESS-COG-CARTO/1_DONNEES_LIVRAISON_2022-04-15\ADECOGC_3-1_SHP_WGS84G_FRA/COMMUNE")
    print('read')
    topo = tp.Topology(sf)
    print("topo done")
    topo.toposimplify(4).to_svg()

    return


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    # to prevent from unuseful loading data
    # shp_to_light_geojson()
    communes_outlines = read_shp_outlines_to_shapely()
    security = True
    if not security:
        pd.set_option('display.max_columns', 40)
        pd.set_option('display.max_rows', 100)
        pd.set_option('display.width', 1500)

        communes_outlines = read_shp_outlines()
        # save_outlines_to_db(communes_outlines)
