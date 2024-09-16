from api_diago.resources.common.database import engine
from sqlalchemy import text, bindparam


def db_request(request, params):
    result = None
    with engine.connect() as conn:
        t = text(request)
        for param, values in params.items():
            t = t.bindparams(bindparam(param, expanding=type(values) is list))
        result = conn.execute(t, params)
    return result

