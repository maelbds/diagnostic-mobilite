import datetime


def message_request(name, geo_codes):
    if name == "topography":
        print(f"{name} - {datetime.datetime.now(datetime.timezone.utc).isoformat(sep=' ', timespec='minutes')}")
    else:
        print(name)
    print(f"{geo_codes[:10]} ... / total : {len(geo_codes)} communes")
