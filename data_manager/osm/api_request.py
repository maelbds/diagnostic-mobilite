"""
OSM API request via Overpass API : http://overpass-api.de/

Useful online version : https://overpass-turbo.eu/
To check status / available queries : http://overpass-api.de/api/status
"""
from data_manager.http_request import post_request


def api_osm_request_train(geo_code):
    """ Inside a commune, get the railways coordinates.

    :param geo_code: INSEE geocode of the concerned commune
    :return: Railways (JSON)
    """
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json];
    area["ref:INSEE"=
    """ + str(geo_code) + """
    ][admin_level=8][boundary=administrative]->.commune;
    (
    way(area.commune)["railway"="rail"]["usage"="main"];
    );
    out tags geom;
    """
    response = post_request(overpass_url, overpass_query)
    r_json = response.json()
    return r_json["elements"]


if __name__ == '__main__':
    print(api_osm_request_train("79048"))

