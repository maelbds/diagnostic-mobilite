def format_persons(persons):
    persons = persons.loc[:, ["geo_code", "id_ind", "id_census_ind", "source_id"]]
    persons = persons.rename(columns={
        "id_census_ind": "id_ind_census",
        "source_id": "id_ind_emp"
    })
    return persons

