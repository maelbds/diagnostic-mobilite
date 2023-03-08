"""
To load data from xls to database | EXECUTE ONCE TO FILL DATABASE
"""
import csv
import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection


def get_car_fleet_from_xls():
    domtom = ['Guadeloupe', 'Martinique', 'Guyane', 'La Réunion', 'Mayotte']
    metropole = ['Île-de-France', 'Centre-Val de Loire',
                 'Bourgogne-Franche-Comté', 'Normandie', 'Hauts-de-France', 'Grand Est', 'Pays de la Loire', 'Bretagne',
                 'Nouvelle-Aquitaine', 'Occitanie', 'Auvergne-Rhône-Alpes', 'Provence-Alpes-Côte d Azur', 'Corse']
    car_fleet_domtom = pd.read_excel("data/2020/rsvero_parcs_vp_2020_france.xlsx",
                                     sheet_name=domtom, skiprows=6,
                                     usecols="A:O", header=None)
    car_fleet_metro = pd.read_excel("data/2020/rsvero_parcs_vp_2020_france.xlsx",
                                    sheet_name=metropole, skiprows=6,
                                    usecols="B:P", header=None)
    car_fleet_domtom = pd.concat(car_fleet_domtom.values())
    car_fleet_metro = pd.concat(car_fleet_metro.values())

    crit1 = "critair1"  # "Crit'Air 1"
    crit2 = "critair2"  # "Crit'Air 2"
    crit3 = "critair3"  # "Crit'Air 3"
    crit4 = "critair4"  # "Crit'Air 4"
    crit5 = "critair5"  # "Crit'Air 5"
    elec = "electrique"  # "Electriques"
    nc = "non_classe"  # Non classés

    mi_tuples = [('geo_code',),
                 ('name',),
                 (crit1, 'Essence'), (crit1, 'Gaz'), (crit1, 'Hybride rechargeable'),
                 (crit2, 'Diesel'), (crit2, 'Essence'),
                 (crit3, 'Diesel'), (crit3, 'Essence'),
                 (crit4, 'Diesel'),
                 (crit5, 'Diesel'),
                 (elec, 'Electrique et Hydrogène'),
                 (nc, 'Autres énergies'), (nc, 'Diesel'), (nc, 'Essence')]
    mi = pd.MultiIndex.from_tuples(mi_tuples)

    car_fleet_domtom.columns = mi
    car_fleet_metro.columns = mi

    car_fleet = pd.concat([car_fleet_domtom, car_fleet_metro])

    to_drop = ["Total département", "ND", "Région"]
    car_fleet = car_fleet.replace({v: None for v in to_drop})
    car_fleet = car_fleet.dropna()
    print(car_fleet)

    car_fleet = car_fleet.groupby(level=0, axis=1).sum()
    car_fleet = car_fleet.drop(columns=["name"])

    car_fleet = car_fleet.groupby("geo_code", as_index=False).sum()

    return car_fleet


def save_data_to_db(data):
    """
    Read data from csv file & add it to the database
    :return:
    """
    conn = mariadb_connection()
    cur = conn.cursor()

    cols_name = "(" + ", ".join([col for col in data.columns]) + ", date, source)"
    values_name = "(" + ", ".join(["?" for col in data.columns]) + ", CURRENT_TIMESTAMP, 'RSVERO_2020')"

    def request(cur, cols):
        cur.execute("""INSERT INTO rsvero_critair """ + cols_name + """ VALUES """ + values_name, cols)

    [request(cur, list(row.values)) for index, row in data.iterrows()]

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------------


if __name__ == "__main__":
    # to prevent from unuseful loading data
    security = True
    if not security:
        pd.set_option('display.max_columns', 40)
        pd.set_option('display.max_rows', 100)
        pd.set_option('display.width', 1500)

        car_fleet = get_car_fleet_from_xls()
        print(car_fleet)
        #save_data_to_db(car_fleet)
