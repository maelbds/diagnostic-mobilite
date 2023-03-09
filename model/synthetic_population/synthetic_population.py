import pandas as pd
import numpy as np

from data_manager.insee_census.census import get_census_from_cantons
from data_manager.insee_general.code_geo_canton import geo_code_to_canton_code
from data_manager.insee_general.density import get_density
from data_manager.insee_general.status import get_uu_status
from model.synthetic_population.allocation import stochastic_rounding
from model.synthetic_population.marginals import get_marginals
from model.synthetic_population.iterative_proportional_updating import iterative_proportional_updating as ipu


def format_census_for_ipu(census, marginals):
    cs_ipu = pd.DataFrame()
    for m in marginals:
        calc = m["calculation"](census)
        for key, value in m["values"].items():
            cs_ipu[key] = calc[key]
    return cs_ipu


def compare_results(cs_ipu_by_households_np, marginals_values, weights, int_weights):
    compare = pd.DataFrame(marginals_values)

    weighted_sum = np.dot(cs_ipu_by_households_np.transpose(), weights)
    compare["weighted"] = [round(ws) for ws in weighted_sum]

    int_weighted_sum = np.dot(cs_ipu_by_households_np.transpose(), int_weights)
    compare["int_weighted"] = [round(ws) for ws in int_weighted_sum]

    compare["relative_difference"] = compare[["marginals", "int_weighted"]].\
        apply(lambda row: round(abs(row["marginals"] - row["int_weighted"])/row["marginals"] * 100) if row["marginals"] != 0 else 0, axis=1)

    print(compare)
    return compare


def get_census_for_ipu(pool, geo_codes):
    cantons = list(set([geo_code_to_canton_code(pool, geo_code) for geo_code in geo_codes]))

    census = get_census_from_cantons(pool, cantons)
    marginals = get_marginals(pool)

    census_ipu = format_census_for_ipu(census, marginals)
    if __name__ == '__main__':
        print("census")
        print(census)
        print("census_ipu")
        print(census_ipu)

    return census, census_ipu


def create_synthetic_population(pool, geo_code, census, census_ipu):
    print(f"Create synthetic population for commune {geo_code}")
    marginals = get_marginals(pool, geo_code)

    marginals_values = dict()
    [marginals_values.update(m["values"]) for m in marginals]
    marginals_values = pd.DataFrame(marginals_values, index=[0]).iloc[0].rename("marginals")

    # order census_ipu to fit with marginals
    census_ipu = census_ipu.loc[:, marginals_values.index.to_list()]

    if __name__ == '__main__':
        print(f"--- marginals value for commune {geo_code}")
        print(marginals_values)

    census_ipu["id_census_hh"] = census['id_census_hh']
    cs_ipu_by_households = census_ipu.groupby(["id_census_hh"]).sum()
    cs_ipu_by_households_np = cs_ipu_by_households.to_numpy()

    # Fitting step
    weights = ipu(cs_ipu_by_households_np, marginals_values)

    # Allocation step
    int_weights = stochastic_rounding(weights)

    #if __name__ == '__main__':
    #compare_results(cs_ipu_by_households_np, marginals_values, weights, int_weights)

    # Fitting step
    weights = ipu(cs_ipu_by_households_np, marginals_values, int_weights)

    # Allocation step
    int_weights = stochastic_rounding(weights)

    #if __name__ == '__main__':
    #compared_results = compare_results(cs_ipu_by_households_np, marginals_values, weights, int_weights)

    cs_ipu_by_households["weights"] = int_weights
    census = pd.merge(census, cs_ipu_by_households["weights"], left_on="id_census_hh", right_index=True)

    synthetic_population = census[census["weights"] != 0].copy()

    hh_id = 0
    while max(synthetic_population["weights"]) > 1:
        hh_id += 1
        mask = synthetic_population["weights"] > 1

        to_add = synthetic_population.loc[mask, :].copy()
        to_add["id_census_hh"] = to_add['id_census_hh'].astype(str) + f"_{hh_id}"
        to_add["weights"] = 1

        synthetic_population.loc[mask, "weights"] = synthetic_population.loc[mask, "weights"] - 1
        synthetic_population = synthetic_population.append(to_add)

    synthetic_population = synthetic_population.drop(columns=["weights"])

    """
    synthetic_population = census.loc[census.index.repeat(census['weights'])].reset_index(drop=True)\
        .drop(columns=["weights"])
    """
    synthetic_population["geo_code"] = geo_code

    commune_uu_status = get_uu_status(pool, geo_code)
    synthetic_population["commune_uu_status"] = commune_uu_status
    commune_density = get_density(pool, geo_code)
    synthetic_population["commune_density"] = commune_density

    synthetic_population["id_hh"] = synthetic_population["id_census_hh"].astype(str) + \
                                    "_" + synthetic_population["geo_code"].astype(str)

    return synthetic_population


def get_synthetic_population(pool, geo_codes):
    """

    :param geo_codes: (List) of communes geo_codes where to create synthetic population
    :return: (DataFrame) of profiles persons from French census which fit communes marginals
    """
    census, census_ipu = get_census_for_ipu(pool, geo_codes)

    synthetic_population_with_results = [create_synthetic_population(pool, geo_code, census, census_ipu)
                                      for geo_code in geo_codes]
    synthetic_population = [s for s in synthetic_population_with_results]
    #results = [s[1] for s in synthetic_population_with_results]

    synthetic_population = pd.concat(synthetic_population)

    # simple id_hh
    ids_hh = synthetic_population["id_hh"].drop_duplicates()
    ids_hh = ids_hh.reset_index(drop=True).rename("id_hh").reset_index()
    synthetic_population = pd.merge(synthetic_population, ids_hh, on="id_hh").\
        drop(columns="id_hh").\
        rename(columns={"index": "id_hh"})
    # simple id
    synthetic_population.reset_index(drop=True, inplace=True)
    synthetic_population["id"] = synthetic_population.index
    # drop unuseful cols
    synthetic_population.drop(columns=["w_census_ind", "id_census_hh", "id_census_ind"], inplace=True)
    # reorder cols
    cols = synthetic_population.columns.tolist()
    cols = cols[-3:][::-1] + cols[:-3]
    synthetic_population = synthetic_population[cols]
    return synthetic_population


if __name__ == '__main__':
    pd.set_option('display.max_columns', 40)
    pd.set_option('display.width', 1500)
    syn_pop = get_synthetic_population(None, ["79048", "79270"])
    print(syn_pop)
    print(syn_pop.head(50))
    print(syn_pop.dtypes)
    mask_sup5 = syn_pop["status"] != "scholars_2_5"
    print(syn_pop[mask_sup5].groupby("status").count()/len(syn_pop[mask_sup5])*100)

