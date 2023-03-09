import numpy as np
import requests


def itinerary_osrm(start_coord, end_coord):
    # In : depart (Zone), arrivee (Zone)
    # Out : coordonnées GPS du trajet pour aller du départ à l'arrivée [[lon],[lat]]

    OSRM_request = "http://router.project-osrm.org/route/v1/driving/{},{};{},{}?overview=simplified&geometries=geojson".format(
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


def address_to_coords(query):
    # API Nominatim
    nominatim_request = " https://nominatim.openstreetmap.org/search?" \
                        "q=" + str(query) + "&" \
                                            "format=json&countrycodes=fr"
    r = requests.get(nominatim_request)
    r_json = r.json()
    if len(r_json) > 0:
        lat = float(r_json[0]["lat"])
        lon = float(r_json[0]["lon"])
        return [lat, lon]
    else:
        print("-- No coords found for address : " + str(query))
        return False
