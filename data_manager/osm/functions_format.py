"""
Functions used in osm/ to format osm api data
"""
import matplotlib.pyplot as plt


def light_osm_data_center(data):
    """
    From osm data response, keeps only coordinates
    :param data: (Json) data response of osm api center
    :return: (List) of coordinates of objects in data [lat, lon]
    """
    light_data = []
    for d in data:
        if "center" in d:
            lat = d["center"]["lat"]
            lon = d["center"]["lon"]
            light_data.append([lat, lon])
    return light_data


def light_osm_data_geom(data):
    """
    From osm data response, keeps only coordinates
    :param data: (Json) data response of osm api geom
    :return: (List) coordinates of boundaries of objects in data [lat, lon]
    """
    light_data = []
    for d in data:
        path = []
        if "geometry" in d:
            for coords in d["geometry"]:
                lat = coords["lat"]
                lon = coords["lon"]
                path.append([lat, lon])
            light_data.append(path)
    return light_data


def process_osm_data_places(json, type):
    """
    :param json: json response from api
    :param type: type of place
    :return: (Dict) with processed data
    """
    result = []
    for e in json:
        if "center" in e:
            lat = e["center"]["lat"]
            lon = e["center"]["lon"]
        else:
            lat = e["lat"]
            lon = e["lon"]
        name = None
        if "tags" in e:
            if "name" in e["tags"]:
                name = e["tags"]["name"]
        if name is not None:
            result.append({
                "lat": lat,
                "lon": lon,
                "name": name,
                "type": type
            })
    return result


def process_osm_data_way(json):
    """
    :param json: json response from api
    :return: (List) with processed data
    """
    ways = []
    for e in json:
        lat = []
        lon = []
        for p in e["geometry"]:
            lat.append(p["lat"])
            lon.append(p["lon"])
        ways.append([lat, lon])

    return ways


def process_osm_data_outline(json):
    """
    :param json: json response from api
    :return: (List) with processed data
    """
    outlines = []
    outline_parts = []

    for m in json[0]["members"]:
        if "geometry" in m.keys():
            outline_part = []
            for p in m["geometry"]:
                outline_part.append([p["lat"], p["lon"]])
            outline_parts.append(outline_part)

    while len(outline_parts) > 0:
        o = outline_parts.pop()
        remains_outline_part = True
        while remains_outline_part:
            part_remaining = False
            for p in outline_parts:
                if o[-1] == p[0]:
                    o.extend(p)
                    outline_parts.remove(p)
                    part_remaining = True
                    break
                elif o[-1] == p[-1]:
                    p.reverse()
                    o.extend(p)
                    p.reverse()
                    outline_parts.remove(p)
                    part_remaining = True
                    break
            if not part_remaining:
                remains_outline_part = False
        outlines.append(o)


    """
    if len(outline_parts) > 0:
        outlines[0].extend(outline_parts.pop())
        while len(outline_parts) > 0:
            for p in outline_parts:
                is_in_current_outlines = False
                for outline in outlines:
                    if outline[-1] == p[0]:
                        outline.extend(p)
                        outline_parts.remove(p)
                        is_in_current_outlines = True
                        break
                    elif outline[-1] == p[-1]:
                        p.reverse()
                        outline.extend(p)
                        p.reverse()
                        outline_parts.remove(p)
                        is_in_current_outlines = True
                        break
                    elif outline[0] == p[0]:
                        outline.reverse()
                        outline.extend(p)
                        outline_parts.remove(p)
                        is_in_current_outlines = True
                        break
                    elif outline[0] == p[-1]:
                        outline.reverse()
                        p.reverse()
                        outline.extend(p)
                        p.reverse()
                        outline_parts.remove(p)
                        is_in_current_outlines = True
                        break
                if not is_in_current_outlines:
                    outlines.append(p)
                    outline_parts.remove(p)"""

    return outlines

