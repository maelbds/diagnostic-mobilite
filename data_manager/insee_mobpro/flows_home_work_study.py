import pprint
import pandas as pd
import numpy as np
import requests

from data_manager.database_connection.sql_connect import mariadb_connection, mariadb_connection_pool
from data_manager.exception import UnknownGeocodeError
from data_manager.ign.commune_center import get_coords
from data_manager.insee_general.districts import get_districts
from data_manager.insee_local.pop_status_nb import get_pop_status_nb
from data_manager.insee_local.topography import get_surface
from data_manager.insee_local.workers_within_commune_prop import get_workers_within_commune_prop
from data_manager.insee_mobpro.flows_home_work import get_flows_home_work
from data_manager.osm.functions_geography import distance_pt_pt

from data_manager.insee_mobpro.source import SOURCE_MOBPRO

WORK_FLOWS_THRESHOLD = 10


def itineraryOSRM(start_coord, end_coord):
    # In : depart (Zone), arrivee (Zone)
    # Out : coordonnées GPS du trajet pour aller du départ à l'arrivée [[lon],[lat]]

    OSRM_request = "http://router.project-osrm.org/route/v1/driving/{},{};{},{}?overview=simplified&geometries=geojson".format( \
        start_coord[1], start_coord[0], end_coord[1], end_coord[0])
    r = requests.get(OSRM_request)
    r_json = r.json()
    coords = r_json["routes"][0]["geometry"]["coordinates"]
    lon = np.array(coords)[:, 0]
    lat = np.array(coords)[:, 1]
    distance = r_json["routes"][0]["legs"][0]["distance"]
    duration = r_json["routes"][0]["legs"][0]["duration"]
    iti = {
        "iti": [lat, lon],
        "distance": distance,
        "duration": duration
    }
    return iti


def calc_estimated_dist(coord1, coord2):
    X = np.array(coord1)
    Y = np.array(coord2)
    conv_deg_km = np.array([np.pi / 180 * 6400, np.pi / 180 * 4400])
    crow_fly_dist = abs(np.linalg.norm(np.multiply(X - Y, conv_deg_km)))
    # To estimate dist via road
    # "From crow-fly distances to real distances, or the origin of detours, Heran"
    dist = crow_fly_dist * (1.1 + 0.3 * np.exp(-crow_fly_dist / 20))
    return dist


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        pd.set_option('display.max_columns', 50)
        pd.set_option('display.max_rows', 50)
        pd.set_option('display.width', 2000)

        cc_val_dauphine = ['38509', '38377', '38315', '38001', '38398', '38381', '38343', '38076', '38401', '38341',
                           '38064', '38560', '38520', '38508', '38464', '38434', '38420', '38369', '38357', '38354',
                           '38323', '38296', '38257', '38246', '38183', '38162', '38148', '38147', '38104', '38098',
                           '38089', '38047', '38044', '38038', '38029', '38012']
        cc_balcon_dauphine = ['38261', '38465', '38050', '38554', '38542', '38539', '38535', '38532', '38515', '38507',
                              '38488', '38467', '38451', '38415', '38392', '38374', '38294', '38282', '38260', '38250',
                              '38210', '38190', '38176', '38146', '38138', '38109', '38067', '38026', '38010', '38546',
                              '38543', '38525', '38494', '38483', '38458', '38365', '38320', '38297', '38295', '38247',
                              '38139', '38135', '38124', '38083', '38055', '38054', '38022']


        marseille_pertuis_luberon = ['84147', '84133', '84113', '84084', '84076', '84026', '84024', '84014', '84010',
                                     '84002', '84151', '84121', '84090', '84052', '84042', '84009', '84089', '84074',
                                     '84093', '84065', '84095', '84068', '84140']
        marseille_baux_provence = ['13076', '13116', '13083', '13066', '13052', '13045', '13036', '13027', '13018',
                                   '13010', '13089', '13067', '13064', '13100', '13094', '13057', '13068', '13038',
                                   '13065', '13058', '13034', '13011', '13006']

        pool = mariadb_connection_pool()

        for epci in [cc_val_dauphine, cc_balcon_dauphine, marseille_pertuis_luberon, marseille_baux_provence]:
            print(epci)
            total_dist = 0
            total_dist_approx = 0
            total_nb = 0
            for commune in epci:
                coords = get_coords(pool, commune)
                for flow in get_flows_home_work(pool, commune):
                    if flow[4]>=20:
                        total_nb += flow[4]
                        total_dist += round(itineraryOSRM(coords, [flow[2], flow[3]])["distance"]/1000, 1) * flow[4]
                        total_dist_approx += round(calc_estimated_dist(coords, [flow[2], flow[3]]), 1) * flow[4]
                nb_within = get_workers_within_commune_prop(pool, commune) * get_pop_status_nb(pool, commune)["employed"]
                dist_within = np.sqrt(get_surface(pool, commune))
                total_nb += nb_within
                total_dist += dist_within*nb_within
                total_dist_approx += dist_within*nb_within
            print("total_nb")
            print(total_nb)
            print("dist/pers")
            print(round(total_dist/total_nb, 1))
            print("dist_approx/pers")
            print(round(total_dist_approx/total_nb, 1))

    except UnknownGeocodeError as e:
        print(e.message)
