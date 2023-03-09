import pandas as pd

from data_manager.database_connection.sql_connect import mariadb_connection_pool
from data_manager.insee_local.csp import get_csp_marginals
from data_manager.insee_local.households_cars_nb import get_households_cars_nb
from data_manager.insee_local.nbenffr import get_nbenffr
from data_manager.insee_local.pop_status_nb import get_pop_status_nb
from data_manager.insee_local.typmr import get_typmr
from data_manager.insee_local.work_travel_mode_prop import get_work_travel_mode_prop
from data_manager.insee_local.workers_within_commune_prop import get_workers_within_commune_prop
from data_manager.insee_mobpro.flows_home_work import get_flows_home_work_trans


def get_marginals(pool, geo_code="79048"):
    """
    marginals = [
        {
            "name": name,
            "value": value,
            "calculation": calc
        }
    ]
    """
    marginals = []

    # --- STATUS
    status = get_pop_status_nb(pool, geo_code)
    status = {"status_" + key: value for (key, value) in status.items()}

    def calc_status(census):
        cs_ipu = pd.DataFrame()
        cs_ipu["status"] = census["status"]
        cs_ipu_status = pd.get_dummies(cs_ipu['status'], prefix_sep='_', prefix='status', dtype=int)
        cs_ipu = cs_ipu.join(cs_ipu_status)
        cs_ipu = cs_ipu.drop(columns=["status"])

        return cs_ipu

    # --- WORKERS WITHIN COMMUNE
    nb_employed = get_pop_status_nb(pool, geo_code)["employed"]
    workers_within_commune_prop = get_workers_within_commune_prop(pool, geo_code)
    workers_within_commune = round(nb_employed * workers_within_commune_prop)
    workers_within_commune = {"workers_within_commune": workers_within_commune}

    def calc_workers_within_commune(census):
        cs_ipu = pd.DataFrame()
        cs_ipu["workers_within_commune"] = census["work_within_commune"]
        return cs_ipu

    # --- WORK TRAVEL MODE
    nb_employed = get_pop_status_nb(pool, geo_code)["employed"]
    a, b, work_travel_mode_prop, c = get_flows_home_work_trans(pool, geo_code)
    work_travel_mode_prop = work_travel_mode_prop["flow"].to_dict()
    work_travel_mode = {"work_travel_mode_" + str(key): round(nb_employed * value) for (key, value)
                        in work_travel_mode_prop.items()}

    def calc_work_travel_mode(census):
        cs_ipu = pd.DataFrame()
        cs_ipu["work_travel_mode"] = census["work_transport"]

        work_travel_mode_ipu = pd.get_dummies(cs_ipu['work_travel_mode'], prefix_sep='_', prefix='work_travel_mode',
                                          dtype=int)
        cs_ipu = cs_ipu.join(work_travel_mode_ipu)
        cs_ipu = cs_ipu.drop(columns=["work_travel_mode_Z"])
        cs_ipu = cs_ipu.drop(columns=["work_travel_mode"])
        return cs_ipu

    # --- CSP
    csp = get_csp_marginals(pool, geo_code)
    csp = {"csp_" + key: value for (key, value) in csp.items()}

    def calc_csp(census):
        cs_ipu = pd.DataFrame()
        cs_ipu["csp"] = census["csp"]
        cs_ipu_csp = pd.get_dummies(cs_ipu['csp'], prefix_sep='_', prefix='csp', dtype=int)
        cs_ipu = cs_ipu.join(cs_ipu_csp)
        cs_ipu = cs_ipu.drop(columns=["csp"])
        return cs_ipu

    # --- CARS NB
    cars_nb = get_households_cars_nb(pool, geo_code)
    cars_nb = {"cars_nb_" + key: value for (key, value) in cars_nb.items()}

    def calc_cars_nb(census):
        cs_ipu = pd.DataFrame()
        cs_ipu["cars_nb"] = census["nb_car"]

        cars_nb_ipu = pd.get_dummies(cs_ipu['cars_nb'], prefix_sep='_', prefix='cars_nb', dtype=int)
        cs_ipu = cs_ipu.join(cars_nb_ipu)
        cs_ipu = cs_ipu.drop(columns=["cars_nb"])

        # BE CAREFUL : nb_car attribute is redundant for each person in a household
        # so we have to divide by nb of persons in household
        cs_ipu = cs_ipu.div(census["nb_pers"], axis=0)
        return cs_ipu

    # --- CHILD NB
    child_nb = get_nbenffr(pool, geo_code)
    child_nb = {"child_nb_" + str(key): value for (key, value) in child_nb.items()}
    child_nb.pop("child_nb_0")

    def calc_child_nb(census):
        cs_ipu = pd.DataFrame()
        cs_ipu["child_nb"] = census["nb_child"]

        child_nb_ipu = pd.get_dummies(cs_ipu['child_nb'], prefix_sep='_', prefix='child_nb', dtype=int)
        cs_ipu = cs_ipu.join(child_nb_ipu)
        cs_ipu = cs_ipu.drop(columns=["child_nb"])

        # BE CAREFUL : CHILD NB attribute is redundant for each person in a household
        # so we have to divide by nb of persons in household
        cs_ipu = cs_ipu.div(census["nb_pers"], axis=0)
        return cs_ipu

    # --- TYPMR
    hh_type = get_typmr(pool, geo_code)
    hh_type = {"hh_type_" + str(key): value for (key, value) in hh_type.items()}

    total_hh_type = sum(hh_type.values())
    total_pop = sum(status.values())

    if total_hh_type != 0:
        new_hh_type = {
            "hh_type_1": round((hh_type["hh_type_1"])*total_pop/total_hh_type),
            "hh_type_2": round((hh_type["hh_type_2"])*total_pop/total_hh_type),
            "hh_type_3": round((hh_type["hh_type_3"])*total_pop/total_hh_type),
            "hh_type_4": round((hh_type["hh_type_4"])*total_pop/total_hh_type),
        }
        hh_type = new_hh_type

    def calc_hh_type(census):
        cs_ipu = pd.DataFrame()
        cs_ipu["hh_type"] = census["hh_type"]

        hh_type_ipu = pd.get_dummies(cs_ipu['hh_type'], prefix_sep='_', prefix='hh_type', dtype=int)
        cs_ipu = cs_ipu.join(hh_type_ipu)
        cs_ipu = cs_ipu.drop(columns=["hh_type"])
        return cs_ipu

    # --- SELECTION OF MARGINALS
    marginals.append({
        "name": "cars_nb",
        "values": cars_nb,
        "calculation": calc_cars_nb
    })
    marginals.append({
        "name": "status",
        "values": status,
        "calculation": calc_status
    })
    marginals.append({
        "name": "csp",
        "values": csp,
        "calculation": calc_csp
    })
    if total_hh_type != 0:
        marginals.append({
            "name": "hh_type",
            "values": hh_type,
            "calculation": calc_hh_type
        })
    marginals.append({
        "name": "child_nb",
        "values": child_nb,
        "calculation": calc_child_nb
    })
    marginals.append({
        "name": "workers_within_commune",
        "values": workers_within_commune,
        "calculation": calc_workers_within_commune
    })
    marginals.append({
        "name": "work_travel_mode",
        "values": work_travel_mode,
        "calculation": calc_work_travel_mode
    })

    return marginals


if __name__ == '__main__':
    pool = mariadb_connection_pool()
    print(get_marginals(pool, "79048"))

