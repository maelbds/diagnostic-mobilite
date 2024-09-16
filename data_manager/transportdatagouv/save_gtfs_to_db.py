import os

import pandas as pd
import numpy as np
from scipy.spatial import Delaunay

from data_manager.database_connection.sql_connect import mariadb_connection
from data_manager.ign.commune_outline import read_shp_outlines_communes
from data_manager.transportdatagouv.gtfs_analysis import gtfs_to_geo_codes


def request_agency_bdd(cursor, datagouv_id, df):
    def request(cur, cols):
        cur.execute("""INSERT INTO datagouv_pt_agency 
                                        (datagouv_id,
                                         agency_id, 
                                         agency_name, 
                                         saved_on) VALUES (?,?,?,CURRENT_TIMESTAMP)""", cols)

    [request(cursor, [datagouv_id] + list(cols))
     for cols in zip(df["agency_id"],
                     df["agency_name"])]


def request_routes_bdd(cursor, datagouv_id, df):
    def request(cur, cols):
        cur.execute("""INSERT INTO datagouv_pt_routes 
                                        (datagouv_id,
                                         route_id, 
                                         agency_id, 
                                         route_short_name, 
                                         route_long_name, 
                                         route_type, 
                                         saved_on) VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)""", cols)

    [request(cursor, [datagouv_id] + list(cols))
     for cols in zip(df["route_id"],
                     df["agency_id"],
                     df["route_short_name"],
                     df["route_long_name"],
                     df["route_type"])]


def request_calendar_bdd(cursor, datagouv_id, df):
    def request(cur, cols):
        cur.execute("""INSERT INTO datagouv_pt_calendar 
                                        (datagouv_id,
                                         service_id, 
                                         monday, 
                                         tuesday, 
                                         wednesday, 
                                         thursday, 
                                         friday, 
                                         saturday, 
                                         sunday, 
                                         start_date, 
                                         end_date, 
                                         saved_on) VALUES (?,?,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)""", cols)

    [request(cursor, [datagouv_id] + list(cols))
     for cols in zip(df["service_id"],
                     df["monday"],
                     df["tuesday"],
                     df["wednesday"],
                     df["thursday"],
                     df["friday"],
                     df["saturday"],
                     df["sunday"],
                     df["start_date"],
                     df["end_date"])]


def request_trips_bdd(cursor, datagouv_id, df):
    def request(cur, cols):
        cur.execute("""INSERT INTO datagouv_pt_trips 
                                        (datagouv_id,
                                         trip_id, 
                                         route_id, 
                                         service_id, 
                                         saved_on) VALUES (?,?,?,?,CURRENT_TIMESTAMP)""", cols)

    [request(cursor, [datagouv_id] + list(cols))
     for cols in zip(df["trip_id"],
                     df["route_id"],
                     df["service_id"])]


def request_stops_bdd(cursor, datagouv_id, df):
    def request(cur, cols):
        cur.execute("""INSERT INTO datagouv_pt_stops 
                                        (datagouv_id,
                                         stop_id, 
                                         stop_name, 
                                         stop_lat, 
                                         stop_lon, 
                                         saved_on) VALUES (?,?,?,?,?,CURRENT_TIMESTAMP)""", cols)

    [request(cursor, [datagouv_id] + list(cols))
     for cols in zip(df["stop_id"],
                     df["stop_name"],
                     df["stop_lat"],
                     df["stop_lon"])]


def request_stop_times_bdd(cursor, datagouv_id, df):
    def request(cur, cols):
        cur.execute("""INSERT INTO datagouv_pt_stop_times 
                                        (datagouv_id,
                                         trip_id, 
                                         stop_id, 
                                         arrival_time, 
                                         departure_time, 
                                         stop_sequence, 
                                         saved_on) VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)""", cols)

    [request(cursor, [datagouv_id] + list(cols))
     for cols in zip(df["trip_id"],
                     df["stop_id"],
                     df["arrival_time"],
                     df["departure_time"],
                     df["stop_sequence"])]


def request_geocodes_bdd(cursor, datagouv_id, df):
    def request(cur, cols):
        cur.execute("""INSERT INTO datagouv_pt_geocodes 
                                        (geo_code,
                                         datagouv_id, 
                                         route_id,
                                         main_trip_id) VALUES (?,?,?,?)""", cols)

    [request(cursor, [geo_code, datagouv_id, route_id, main_trip_id])
     for geo_code, route_id, main_trip_id in zip(df["geo_code"], df["route_id"], df["main_trip_id"])]


def save_gtfs_to_db(pool, folder_name, datagouv_id, communes_outline):
    try:
        conn = mariadb_connection(pool)
        cur = conn.cursor()

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        try:
            # agency
            agency_df = pd.read_csv(folder_name + "/agency.txt", sep=",", dtype="str")
            if "agency_id" not in agency_df.columns:
                agency_df["agency_id"] = 0
            agency_df = agency_df.fillna(value={"agency_id": 0})  # in case of no agency_id
            request_agency_bdd(cur, datagouv_id, agency_df)

            # routes
            routes_df = pd.read_csv(folder_name + "/routes.txt", sep=",", dtype="str", keep_default_na=False)
            routes_df = routes_df.fillna(value={"agency_id": 0})  # in case of no agency_id
            routes_df = routes_df.drop_duplicates()
            if "agency_id" not in routes_df.columns:
                agency_id = agency_df["agency_id"].iloc[0]
                routes_df["agency_id"] = agency_id
            request_routes_bdd(cur, datagouv_id, routes_df)

            # calendar
            if os.path.isfile(folder_name + "/calendar.txt"):
                calendar_df = pd.read_csv(folder_name + "/calendar.txt", sep=",", dtype="str", keep_default_na=False)
                calendar_df = calendar_df.drop_duplicates()
                request_calendar_bdd(cur, datagouv_id, calendar_df)
            elif os.path.isfile(folder_name + "/calendar_dates.txt"):
                calendar_dates_df = pd.read_csv(folder_name + "/calendar_dates.txt", sep=",", dtype="str", keep_default_na=False)
                calendar_dates_df = calendar_dates_df.drop_duplicates()
                calendar_df = calendar_dates_df.groupby(by="service_id", as_index=False).agg(**{
                    "start_date": pd.NamedAgg(column="date", aggfunc="min"),
                    "end_date": pd.NamedAgg(column="date", aggfunc="max"),
                })
                calendar_df["monday"] = None
                calendar_df["tuesday"] = None
                calendar_df["wednesday"] = None
                calendar_df["thursday"] = None
                calendar_df["friday"] = None
                calendar_df["saturday"] = None
                calendar_df["sunday"] = None
                request_calendar_bdd(cur, datagouv_id, calendar_df)
            else:
                raise FileNotFoundError("calendar and calendar_dates don't exist")

            # trips
            trips_df = pd.read_csv(folder_name + "/trips.txt", sep=",", dtype="str", keep_default_na=False)
            trips_df = trips_df.drop_duplicates()
            #trips_df = pd.merge(calendar_df["service_id"], trips_df, on="service_id")
            request_trips_bdd(cur, datagouv_id, trips_df)

            # stops
            stops_df = pd.read_csv(folder_name + "/stops.txt", sep=",", dtype="str")
            stops_df = stops_df.drop_duplicates()
            stops_df = stops_df.dropna(subset=['stop_lat', 'stop_lon'])

            stops_df["stop_lat"] = stops_df["stop_lat"].astype("float64")
            stops_df["stop_lon"] = stops_df["stop_lon"].astype("float64")

            """if stops_df["stop_lat"].min() > 47 or stops_df["stop_lat"].max() < 44 \
                    or stops_df["stop_lon"].min() > 7.2 or stops_df["stop_lon"].max() < 2:
                raise Exception("all stops outside AURA region")"""

            request_stops_bdd(cur, datagouv_id, stops_df)

            # stop_times
            stop_times_df = pd.read_csv(folder_name + "/stop_times.txt", sep=",", dtype="str", keep_default_na=False)
            stop_times_df = stop_times_df.drop_duplicates()
            stop_times_df = stop_times_df.replace("", None)
            request_stop_times_bdd(cur, datagouv_id, stop_times_df)

            geo_codes = gtfs_to_geo_codes(datagouv_id, routes_df, trips_df, stops_df, stop_times_df, communes_outline)

            """departements = [g[:2] for g in geo_codes["geo_code"]]
            print(departements)
            dep_aura = ["03", "63", "15", "43", "42", "69", "01", "38", "26", "07", "73", "74"]
            departements_in_aura = [dep in dep_aura for dep in departements]

            if sum(departements_in_aura) == 0:
                raise Exception("all stops outside AURA region")"""

            request_geocodes_bdd(cur, datagouv_id, geo_codes)

            conn.commit()

        except Exception as e:
            print(e)
            print(f"Processing problem with GTFS dataset {datagouv_id} ")

        conn.close()
        print(f"Dataset GTFS with datagouv_id {datagouv_id} processed and saved into database")
    except Exception as e:
        print(e)
        print(f"Database problem to save GTFS {datagouv_id} into database")

# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 2000)


    communes_outline = read_shp_outlines_communes()
    communes_outline["minx"] = communes_outline["outline"].apply(lambda shape: shape.bounds[0])
    communes_outline["miny"] = communes_outline["outline"].apply(lambda shape: shape.bounds[1])
    communes_outline["maxx"] = communes_outline["outline"].apply(lambda shape: shape.bounds[2])
    communes_outline["maxy"] = communes_outline["outline"].apply(lambda shape: shape.bounds[3])

    print(communes_outline)

    save_gtfs_to_db(None,
                    "pt/TAM_MMM_GTFS",
                    "metropole_montpellier",
                    communes_outline)

