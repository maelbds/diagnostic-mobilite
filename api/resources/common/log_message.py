import datetime


def message_request(name, geo_codes):
    if name == "geography":
        print(f"{name} - {datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).isoformat(sep=' ', timespec='minutes')}")
    else:
        print(name)
    print(f"{geo_codes[:10]} ... / total : {len(geo_codes)} communes")
