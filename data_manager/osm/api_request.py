"""
OSM API request via Overpass API : http://overpass-api.de/

Useful online version : https://overpass-turbo.eu/
To check status / available queries : http://overpass-api.de/api/status
"""
from data_manager.http_request import post_request


def api_osm_request_center(geo_code, category, tags):
    """ Inside a commune, get the places with given category and returns with their name & center coordinates.

    :param geo_code: INSEE geocode of the concerned commune
    :param category: OSM category
    :param tags: OSM tags
    :return: List of places (JSON)
    """
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json];
    area["ref:INSEE"=
    """ + str(geo_code) + """
    ][admin_level=8][boundary=administrative]->.commune;
    (
    """
    for a in tags:
        overpass_query += """
        node(area.commune)[""" + category + """ = """ + a + """];
        way(area.commune)[""" + category + """ = """ + a + """];
        rel(area.commune)[""" + category + """ = """ + a + """];
        """
    overpass_query += """
    );
    out tags center;
    """
    response = post_request(overpass_url, overpass_query)
    r_json = response.json()
    return r_json["elements"]


def api_osm_request_geom(geo_code, category, tags):
    """ Inside a commune, get the places with given category and returns with their name & boundary coordinates.

    :param geo_code: INSEE geocode of the concerned commune
    :param category: OSM category
    :param tags: OSM tags
    :return: List of places (JSON)
    """
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json];
    area["ref:INSEE"=
    """ + str(geo_code) + """
    ][admin_level=8][boundary=administrative]->.commune;
    (
    """
    for a in tags:
        overpass_query += """
        way(area.commune)[""" + category + """ = """ + a + """];
        rel(area.commune)[""" + category + """ = """ + a + """];
        """
    overpass_query += """
    );
    out tags geom;
    """
    response = post_request(overpass_url, overpass_query)
    r_json = response.json()
    return r_json["elements"]


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


def api_osm_request_commune_outline(geo_code):
    """ Get the outline/boundary of a commune with given Geocode.

    :param geo_code: INSEE geocode of the concerned commune
    :return: Outline (JSON)
    """
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json];
    rel["ref:INSEE"=
    """ + str(geo_code) + """
    ][admin_level=8][boundary=administrative];

    out body geom;
    """
    response = post_request(overpass_url, overpass_query)
    r_json = response.json()
    return r_json["elements"]


# ---------------------------


def API_OSM_request_area(geo_codes, category, tags, radius):
    overpass_url = "https://overpass-api.de/api/interpreter"

    overpass_query = """
    [out:json];
    ("""
    for geo_code in geo_codes:
        overpass_query += """
        area["ref:INSEE"=""" + str(geo_code) + """][admin_level=8][boundary=administrative];"""
    overpass_query += """)->.a1;
    ("""
    for geo_code in geo_codes:
        overpass_query += """
        rel["ref:INSEE"=""" + str(geo_code) + """][admin_level=8][boundary=administrative];"""
    overpass_query += """)->.a2;
    (
    """
    for a in tags:
        overpass_query += """
        node(area.a1)[""" + category + """ = """ + a + """];
        way(area.a1)[""" + category + """ = """ + a + """];
        rel(area.a1)[""" + category + """ = """ + a + """];
        node(around.a2:""" + str(radius) + """)[""" + category + """ = """ + a + """];
        way(around.a2:""" + str(radius) + """)[""" + category + """ = """ + a + """];
        rel(around.a2:""" + str(radius) + """)[""" + category + """ = """ + a + """];
        """
    overpass_query += """
    )->.b;
    .b out tags center;
    """
    response = request(overpass_url, overpass_query)
    r_json = response.json()
    return r_json["elements"]



