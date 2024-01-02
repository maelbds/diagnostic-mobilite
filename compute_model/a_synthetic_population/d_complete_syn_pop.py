from compute_model.v_database_connection.db_request import db_request


def get_uu_status(geo_code):
    result = db_request(
        """ SELECT status_code
            FROM insee_communes_status 
            WHERE geo_code = :geo_code
        """,
        {
            "geo_code": geo_code,
        }
    )
    return result.scalar_one_or_none()


def get_density(geo_code):
    result = db_request(
        """ SELECT density_code
            FROM insee_communes_density 
            WHERE geo_code = :geo_code
        """,
        {
            "geo_code": geo_code,
        }
    )
    return result.scalar_one_or_none()


def complete_syn_pop(geo_code, syn_pop):
    syn_pop["geo_code"] = geo_code
    syn_pop["commune_uu_status"] = get_uu_status(geo_code)
    syn_pop["commune_density"] = get_density(geo_code)
    return syn_pop

