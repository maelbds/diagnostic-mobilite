import datetime
from flask import request, session
from uuid import uuid4

from api.resources.common.db_request import db_request


def log_stats(name, geo_codes, mesh, year):
    ip = request.remote_addr

    if "session_id" not in session:
        session["session_id"] = str(uuid4())
    session_id = session["session_id"]
    print(session_id)

    db_request(
        """ INSERT INTO stats_api
            (ip, session_id, name, geo_codes, mesh, year, datetime)
            VALUES (:ip, :session_id, :name, :geo_codes, :mesh, :year, :datetime)
            """,
        {
            "ip": ip,
            "session_id": session_id,
            "name": name,
            "geo_codes": "-".join(geo_codes),
            "mesh": mesh,
            "year": year,
            "datetime": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))),
        }
    )



