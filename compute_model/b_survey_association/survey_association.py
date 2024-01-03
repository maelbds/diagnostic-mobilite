import pandas as pd

from compute_model.a_synthetic_population.synthetic_population import get_synthetic_population
from compute_model.b_survey_association.a_anchor_syn_pop import set_residential_areas, set_characteristic_areas
from compute_model.b_survey_association.b_distance_matrix import compute_distance_matrix
from compute_model.b_survey_association.c_commuter_matrix import get_commuter_matrix
from compute_model.b_survey_association.d_set_matching_attributes import set_matching_attributes
from compute_model.b_survey_association.e_emp import get_emp_persons, get_emp_travels
from compute_model.b_survey_association.f_match_syn_pop_emp import match_syn_pop_with_emp
from compute_model.b_survey_association.g_anchor_travels_primary_loc import set_residential_location, \
    match_education_location, match_other_location, match_work_location
from compute_model.b_survey_association.h_anchor_travels_secondary_loc import match_secondary_location
from compute_model.b_survey_association.i_format_travels import compute_distance, compute_ori_des_geocode, \
    format_travels
from compute_model.b_survey_association.j_database import save_travels, save_travels_analysis
from compute_model.c_analysis.a_travels_analysis import analyse_travels
from compute_model.v_database_connection.db_request import db_request
from compute_model.t_territory.a_residential_areas import get_residential_areas
from compute_model.t_territory.b_public_transport import get_pt_stops
from compute_model.t_territory.c_perimeter import get_influence_communes_geo_codes, get_work_communes_geo_codes
from compute_model.t_territory.d_flows_home_work import get_flows_home_work
from compute_model.t_territory.e_places_areas import get_cluster_areas
from compute_model.t_territory.f_work_areas import get_work_areas


def compute_travels_demand(geo_codes, emp_persons, emp_travels):
    syn_pop = pd.concat([get_synthetic_population(g) for g in geo_codes])

    # emp concerns only people older than 5yo
    mask_plus5years = syn_pop["age"] > 5
    syn_pop = syn_pop.loc[mask_plus5years]

    # prerequisites
    work_flows = get_flows_home_work(geo_codes)
    geo_codes_influence = get_influence_communes_geo_codes(geo_codes)
    geo_codes_work = get_work_communes_geo_codes(geo_codes, geo_codes_influence, work_flows)

    # areas and places
    residential_areas = get_residential_areas(geo_codes)
    print(f" - residential areas : {len(residential_areas)}")
    cluster_areas = get_cluster_areas(geo_codes + geo_codes_influence + geo_codes_work)
    print(f" - cluster areas : {len(cluster_areas)}")
    work_areas = get_work_areas(geo_codes + geo_codes_influence + geo_codes_work)
    print(f" - work areas : {len(work_areas)}")
    all_areas = pd.concat([residential_areas, cluster_areas, work_areas])
    pt_stops = get_pt_stops(geo_codes + geo_codes_influence)
    print(f" - pt stops : {len(pt_stops)}")

    # distance matrix
    dist_matrix_ra_stops = compute_distance_matrix(residential_areas, pt_stops)
    print(" - dist matrix stops")
    dist_matrix_areas = compute_distance_matrix(all_areas)
    print(" - dist matrix areas")

    # commuter matrix
    commuter_matrix = get_commuter_matrix(work_flows, work_areas)
    print(" - commuter matrix")

    # enrich syn pop : territorial anchorage
    # - set residential areas
    syn_pop = set_residential_areas(syn_pop, residential_areas)
    print(" - set residential areas")
    # - set characteristic activities areas
    syn_pop = set_characteristic_areas(syn_pop, all_areas, dist_matrix_areas, commuter_matrix)
    print(" - set characteristic area")

    # compute matching attributes
    syn_pop = set_matching_attributes(syn_pop, dist_matrix_ra_stops)
    print(" - matching attributes")

    # matching with emp survey
    syn_pop = match_syn_pop_with_emp(syn_pop, emp_persons)
    print(" - matching emp")

    if __name__ == '__main__':
        print(all_areas)
        print(dist_matrix_ra_stops)
        print(dist_matrix_areas)
        print(syn_pop)

    # adjust ponderation coef of EMP travels
    emp_travels = pd.merge(emp_travels, emp_persons[["id_ind", "w_ind"]], on="id_ind", how="left")
    emp_travels["w_trav"] = emp_travels["w_trav"] / emp_travels["w_ind"]
    emp_travels = emp_travels.drop(columns=["w_ind"])

    # LIST OF ALL TRAVELS
    syn_pop_travels = pd.merge(syn_pop, emp_travels.set_index("id_ind"), left_on="source_id", right_index=True)
    print(" - all travels")

    # TRAVELS TERRITORY ANCHORAGE
    # 1 - associate primary locations
    syn_pop_travels = set_residential_location(syn_pop_travels)
    print(" - set ra loc")
    syn_pop_travels = match_work_location(syn_pop_travels)
    print(" - set work loc")
    syn_pop_travels = match_education_location(syn_pop_travels)
    print(" - set educ loc")
    syn_pop_travels = match_other_location(syn_pop_travels)
    print(" - set other loc")

    # 3 - associate secondary locations
    syn_pop_travels = match_secondary_location(syn_pop_travels, all_areas, dist_matrix_areas)
    print(" - set secondary loc")

    # 4 - format travels
    syn_pop_travels = compute_distance(syn_pop_travels, dist_matrix_areas)
    syn_pop_travels = compute_ori_des_geocode(syn_pop_travels, all_areas)
    syn_pop_travels_f = format_travels(syn_pop_travels)

    if __name__ == '__main__':
        print(syn_pop_travels)
        print(syn_pop_travels_f)

    print("analyse")
    analysis = analyse_travels(syn_pop_travels)

    return syn_pop_travels_f, analysis


if __name__ == '__main__':
    pd.set_option('display.max_columns', 60)
    pd.set_option('display.max_rows', 60)
    pd.set_option('display.width', 2000)
    result = db_request(
        """ SELECT COM
            FROM insee_cog_communes
            WHERE CAN = '0101'
        """,
        {}
    )
    geocodes = pd.DataFrame(result, columns=["geo_code"])["geo_code"].to_list()

    emp_persons = get_emp_persons()
    emp_travels = get_emp_travels()

    travels, analysis = compute_travels_demand(geocodes, emp_persons, emp_travels)

