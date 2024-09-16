import pandas as pd
import numpy as np

from compute_model.years import COG_census, year_census
from compute_model.database_connection.db_request import db_request
from compute_model.a_synthetic_population.a_census import get_census
from compute_model.a_synthetic_population.b_marginals import prepare_census_for_ipu, get_marginals
from compute_model.a_synthetic_population.c2_allocation import stochastic_rounding
from compute_model.a_synthetic_population.c1_iterative_proportional_updating import iterative_proportional_updating as ipu
from compute_model.a_synthetic_population.d_complete_syn_pop import complete_syn_pop
from compute_model.a_synthetic_population.e_format_syn_pop import format_syn_pop


def compute_synthetic_population(geo_code):
    # a. Get census from which syn pop is computed
    census = get_census(geo_code)
    census_ipu = prepare_census_for_ipu(census)

    # b. Get marginals of attributes to match with commune
    marginals = get_marginals(geo_code)

    # order census_ipu to correspond with marginals
    census_ipu = census_ipu.loc[:, marginals.index.to_list()]

    # the ipu is done based on households cause some matching attributes concern the whole household (ex: nb_cars)
    census_ipu["id_census_hh"] = census['id_census_hh']
    census_ipu_hh = census_ipu.groupby(["id_census_hh"]).sum()

    # c. Finding weights
    # c1. Fitting step 1st round
    weights = ipu(census_ipu_hh.to_numpy(), marginals.to_list())
    # c2. Allocation step 1st round
    int_weights = stochastic_rounding(weights)

    # c1. Fitting step 2nd round
    weights = ipu(census_ipu_hh.to_numpy(), marginals.to_list(), int_weights)
    # c2. Allocation step 2nd round
    int_weights = stochastic_rounding(weights)

    quality = compare_results(census_ipu_hh, marginals, weights, int_weights)

    census_ipu_hh["weights"] = int_weights
    census_weighted = pd.merge(census, census_ipu_hh["weights"],
                      left_on="id_census_hh", right_index=True) # census_ipu_hh index is id_census_hh

    return census_weighted, quality


def compare_results(census_ipu_hh, marginals, weights, int_weights):
    compare = pd.DataFrame(marginals.rename("marginals"))

    weighted_sum = census_ipu_hh.mul(weights, axis=0).sum(axis=0).round()
    compare["weighted"] = weighted_sum

    int_weighted_sum = census_ipu_hh.mul(int_weights, axis=0).sum(axis=0).round()
    compare["int_weighted"] = int_weighted_sum

    compare["relative_difference"] = compare[["marginals", "int_weighted"]].\
        apply(lambda row: round(abs(row["marginals"] - row["int_weighted"])/row["marginals"] * 100) if row["marginals"] != 0 else 0, axis=1)

    # print(compare)
    mask_marginal_30 = compare["marginals"] > 30
    mask_marginal_50 = compare["marginals"] > 50
    mask_marginal_100 = compare["marginals"] > 100
    c_rel_diff = compare["relative_difference"]
    c_marginals = compare["marginals"]
    c_rel_diff_30 = compare.loc[mask_marginal_30, "relative_difference"]
    c_marginals_30 = compare.loc[mask_marginal_30, "marginals"]
    c_rel_diff_50 = compare.loc[mask_marginal_50, "relative_difference"]
    c_marginals_50 = compare.loc[mask_marginal_50, "marginals"]
    c_rel_diff_100 = compare.loc[mask_marginal_100, "relative_difference"]
    c_marginals_100 = compare.loc[mask_marginal_100, "marginals"]

    def compute_pond_rel_diff(c_rel_diff_, c_marginals_):
        if len(c_marginals_) > 0:
            pond = c_rel_diff_.mul(c_marginals_).sum() / c_marginals_.sum()
        else:
            pond = None
        return pond

    quality = pd.DataFrame({
        "rel_diff_mean": c_rel_diff.mean(),
        "pond_rel_diff_mean": compute_pond_rel_diff(c_rel_diff, c_marginals),
        "rel_diff_max": c_rel_diff.max(),
        "rel_diff_max_marginal": c_marginals.loc[c_rel_diff.idxmax()],

        "rel_diff_mean_30": c_rel_diff_30.mean(),
        "pond_rel_diff_mean_30": compute_pond_rel_diff(c_rel_diff_30, c_marginals_30),
        "rel_diff_max_30": c_rel_diff_30.max(),
        "rel_diff_max_marginal_30": c_marginals_30.loc[c_rel_diff_30.idxmax()] if len(c_rel_diff_30) > 0 else None,

        "rel_diff_mean_50": c_rel_diff_50.mean(),
        "pond_rel_diff_mean_50": compute_pond_rel_diff(c_rel_diff_50, c_marginals_50),
        "rel_diff_max_50": c_rel_diff_50.max(),
        "rel_diff_max_marginal_50": c_marginals_50.loc[c_rel_diff_50.idxmax()] if len(c_rel_diff_50) > 0 else None,

        "rel_diff_mean_100": c_rel_diff_100.mean(),
        "pond_rel_diff_mean_100": compute_pond_rel_diff(c_rel_diff_100, c_marginals_100),
        "rel_diff_max_100": c_rel_diff_100.max(),
        "rel_diff_max_marginal_100": c_marginals_100.loc[c_rel_diff_100.idxmax()] if len(c_rel_diff_100) > 0 else None,
    }, index=[0]).round(1)
    return quality


def get_synthetic_population(geo_code):
    result = db_request(
        """ SELECT s.id_census_ind, c.id_census_hh, c.SEXE, c.AGED, c.csp, c.status, 
                   c.INPER, c.nb_child, c.hh_type, c.nb_car, c.TRANS, c.work_within_commune,
                   s.weights
            FROM computed_syn_pop AS s
            JOIN insee_census AS c ON s.id_census_ind = c.id 
            WHERE s.geo_code = :geo_code 
            AND c.year_data = :year_data
            AND c.year_cog = :year_cog
        """,
        {
            "geo_code": geo_code,
            "year_data": year_census,
            "year_cog": COG_census
        }
    )
    syn_pop = pd.DataFrame(result, columns=[
        "id_census_ind", "id_census_hh", "sexe", "age", "csp", "status",
        "nb_pers", "nb_child", "hh_type", "nb_car", "work_transport", "work_within_commune",
        "weights"])

    duplicated_index = np.repeat(syn_pop.index, syn_pop["weights"])
    syn_pop = syn_pop.loc[duplicated_index].reset_index(drop=True).drop(columns=["weights"])

    syn_pop = complete_syn_pop(geo_code, syn_pop)
    syn_pop = format_syn_pop(syn_pop)

    return syn_pop


if __name__ == '__main__':
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.width', 1500)
    syn_pop = get_synthetic_population("79048")
    print(syn_pop)
    print(syn_pop.groupby("status").count())


