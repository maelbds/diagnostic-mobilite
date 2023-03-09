import pandas as pd


def set_residential_area(communes, synthetic_population):
    def set_ra_by_commune(commune, syn_pop):
        pop = len(syn_pop.index)
        ra_ids = sum([ra.mass * [ra.id] for ra in 2*commune.residential_areas], [])
        syn_pop["ra_id"] = ra_ids[:pop]
        hh_ra = syn_pop.loc[:, ["id_hh", "ra_id"]].drop_duplicates(subset=["id_hh"])
        return hh_ra

    residential_areas = [
        set_ra_by_commune(c, synthetic_population.loc[synthetic_population.loc[:, "geo_code"] == c.geo_code].copy())
        for c in communes]
    residential_areas = pd.concat(residential_areas, ignore_index=True)
    synthetic_population = pd.merge(synthetic_population, residential_areas, on="id_hh")
    return synthetic_population
