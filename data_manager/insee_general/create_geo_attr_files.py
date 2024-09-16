import pandas as pd

from pyproj import Transformer

from api.resources.common.db_request import db_request


folder = "selection_map_files"


def create_epci_attr(year_cog):
    result = db_request(
        """ SELECT EPCI, LIBEPCI
            FROM insee_epci
            WHERE year_cog = :year_cog 
        """,
        {
            "year_cog": year_cog
        }
    )
    epcis = pd.DataFrame(result, columns=["epci", "epci_name"])
    print(epcis)

    epcis.to_csv(f"{folder}/{year_cog}/epci_attr.csv", index=False)


def create_communes_attr(year_cog):
    result = db_request(
        """ SELECT cog.COM, cog.LIBELLE, cog.ARR, cog.DEP, cog.REG, epci.EPCI,
            aav.AAV, aav.CATEAAV, aav2.TAAV, 
            centroid_lat, centroid_lon, chflieu_lat, chflieu_lon
            FROM insee_cog_communes AS cog
            LEFT JOIN insee_epci_communes AS epci ON cog.COM = epci.CODGEO
            LEFT JOIN insee_aav_communes AS aav ON cog.COM = aav.CODGEO
            LEFT JOIN insee_aav AS aav2 ON aav.AAV = aav2.AAV
            LEFT JOIN ign_commune_center AS ign ON cog.COM = ign.geo_code
            WHERE cog.year_cog = :year_cog 
            AND epci.year_cog = :year_cog
            AND aav.year_cog = :year_cog
            AND aav2.year_cog = :year_cog
            AND ign.year_cog = :year_cog
        """,
        {
            "year_cog": "2023"
        }
    )
    communes = pd.DataFrame(result, columns=["geo_code", "name", "arr", "dep", "reg", "epci",
                                             "aav", "cate_aav", "typo_aav",
                                             "centroid_lat", "centroid_lon", "chflieu_lat", "chflieu_lon"])
    print(communes[communes["geo_code"]=="27676"])

    mask_no_chflieu = communes["chflieu_lat"].isna() | communes["chflieu_lon"].isna()
    communes.loc[mask_no_chflieu, "chflieu_lat"] = communes.loc[mask_no_chflieu, "centroid_lat"]
    communes.loc[mask_no_chflieu, "chflieu_lon"] = communes.loc[mask_no_chflieu, "centroid_lon"]
    communes = communes.drop(columns=["centroid_lat", "centroid_lon"])
    communes = communes.rename(columns={"chflieu_lat": "cheflieu_y", "chflieu_lon": "cheflieu_x"})


    proj_drom = {
        "guadeloupe": {
            "reg": "01",
            "x": 6355000,
            "y": 3330000,
            "scale": 1.5,
        },
        "martinique": {
            "reg": "02",
            "x": 6480000,
            "y": 3505000,
            "scale": 1.5,
        },
        "guyane": {
            "reg": "03",
            "x": 5755000,
            "y": 4665000,
            "scale": 0.35,
        },
        "réunion": {
            "reg": "04",
            "x": -6170000,
            "y": 7560000,
            "scale": 1.5,
        },
    }

    t4326_to_3857 = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
    t3857_to_4326 = Transformer.from_crs("epsg:3857", "epsg:4326", always_xy=True)

    for d in proj_drom.values():
        mask = communes["reg"] == d["reg"]
        print(communes.loc[mask])
        new_coords = communes.loc[mask, ["cheflieu_x", "cheflieu_y"]].apply(lambda row: t4326_to_3857.transform(row[0], row[1]), axis=1)
        print(new_coords)
        communes.loc[mask, "cheflieu_x"] = new_coords.apply(lambda r: r[0] + d["x"])
        communes.loc[mask, "cheflieu_y"] = new_coords.apply(lambda r: r[1] + d["y"])
        communes.loc[mask, "cheflieu_x"] = (communes.loc[mask, "cheflieu_x"] - communes.loc[mask, "cheflieu_x"].mean()) * d["scale"] + communes.loc[mask, "cheflieu_x"].mean()
        communes.loc[mask, "cheflieu_y"] = (communes.loc[mask, "cheflieu_y"] - communes.loc[mask, "cheflieu_y"].mean()) * d["scale"] + communes.loc[mask, "cheflieu_y"].mean()
        print(communes.loc[mask])
        new_coords = communes.loc[mask, ["cheflieu_x", "cheflieu_y"]].apply(lambda row: t3857_to_4326.transform(row[0], row[1]), axis=1)
        communes.loc[mask, "cheflieu_x"] = new_coords.apply(lambda r: r[0])
        communes.loc[mask, "cheflieu_y"] = new_coords.apply(lambda r: r[1])
        print(communes.loc[mask])

    # Mercator projection
    new_coords = communes[["cheflieu_x", "cheflieu_y"]].apply(
        lambda row: t4326_to_3857.transform(row[0], row[1]), axis=1)
    communes["cheflieu_x"] = new_coords.apply(lambda r: r[0])
    communes["cheflieu_y"] = new_coords.apply(lambda r: r[1])

    communes["aav"] = communes["aav"].fillna("0000")
    print(communes)

    communes["typo_aav"] = [f"{cate_aav[0]}{typo_aav}" for cate_aav, typo_aav in zip(communes["cate_aav"], communes["typo_aav"])]

    communes.to_csv(f"{folder}/{year_cog}/communes_attr.csv", index=False)


def create_arr_attr(year_cog):
    result = db_request(
        """ SELECT ARR, CHEFLIEU, LIBELLE
            FROM insee_cog_arrondissements
            WHERE year_cog = :year_cog 
        """,
        {
            "year_cog": year_cog
        }
    )
    arrondissements = pd.DataFrame(result, columns=["arr", "arr_chef_lieu", "arr_name"])
    print(arrondissements)

    arrondissements.to_csv(f"{folder}/{year_cog}/arrondissements_attr.csv", index=False)


def create_dep_attr(year_cog):
    result = db_request(
        """ SELECT DEP, CHEFLIEU, LIBELLE
            FROM insee_cog_departements
            WHERE year_cog = :year_cog 
        """,
        {
            "year_cog": year_cog
        }
    )
    dep = pd.DataFrame(result, columns=["dep", "dep_chef_lieu", "dep_name"])
    print(dep)

    dep.to_csv(f"{folder}/{year_cog}/departements_attr.csv", index=False)


def create_aav_attr(year_cog):
    result = db_request(
        """ SELECT AAV, LIBAAV, TAAV
            FROM insee_aav
            WHERE year_cog = :year_cog 
        """,
        {
            "year_cog": year_cog
        }
    )
    aav = pd.DataFrame(result, columns=["aav", "aav_name", "aav_type"])
    print(aav)

    aav.to_csv(f"{folder}/{year_cog}/aav_attr.csv", index=False)


if __name__ == '__main__':
    year_cog = 2023
    create_epci_attr(year_cog)
    #create_communes_attr(year_cog)
    create_arr_attr(year_cog)
    create_dep_attr(year_cog)
    create_aav_attr(year_cog)

