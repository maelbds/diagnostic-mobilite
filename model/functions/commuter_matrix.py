import pandas as pd
import numpy as np


def build_commuter_matrix(communes, influence_communes, work_communes):
    def set_value(df, row, col, value):
        df.loc[row, col] = value

    # DataFrame with nb of employed people for each commune
    nb_employed_people = pd.DataFrame()
    [set_value(nb_employed_people, c.geo_code, "nb_employed", c.status["employed"]) for c in communes]

    all_geocodes = [c.geo_code for c in communes + influence_communes + work_communes]

    work_areas = {c.geo_code: c.work_areas for c in communes + influence_communes + work_communes}

    def manage_flows(geo_code_o, geo_code_d, flow):
        w_areas = work_areas[geo_code_d]
        total_jobs_nb = sum([wa.jobs_nb for wa in w_areas])
        [set_value(known_flows, geo_code_o, wa.id, round(flow * wa.jobs_nb / total_jobs_nb))
         for wa in w_areas]

    known_flows = pd.DataFrame()
    # known flows outside commune
    [[manage_flows(c.geo_code, geo_code_d, flow)
      for geo_code_d, name, lat, lon, flow in c.flows_home_work if geo_code_d in all_geocodes] for c in communes]
    # known flow within commune
    [manage_flows(c.geo_code, c.geo_code,
                  round(c.workers_within_commune_prop * c.status["employed"])) for c in communes]
    known_flows = known_flows.fillna(0)
    if __name__ == '__main__':
        print(known_flows)

    # Now we want to complete missing data using Universal Opportunity Model
    all_work_areas = []
    [[all_work_areas.append(wa) for wa in w_areas if wa.id in known_flows.columns] for w_areas in work_areas.values()]
    distances = build_distances_matrix_od(communes, all_work_areas)

    uo_flows = universal_opportunity_model(communes, all_work_areas, distances)
    # compute prop
    [[set_value(uo_flows, row, col, 0) for row in known_flows.index if known_flows.loc[row, col] != 0]
     for col in known_flows.columns]
    uo_flows = uo_flows.fillna(0)
    uo_flows = uo_flows.apply(lambda row: row / row.sum() if row.sum() != 0 else row, axis=1)
    if __name__ == '__main__':
        print(uo_flows)

    """
    commuter_matrix = known_flows.copy()
    [[set_value(commuter_matrix, row, col,
                max(0, round(uo_flows.loc[row, col] * (
                        nb_employed_people.loc[row, "nb_employed"] - known_flows.sum(axis=1).loc[row]))))
      for col in uo_flows.columns if uo_flows.loc[row, col] != 0] for row in uo_flows.index]"""

    commuter_matrix = known_flows.apply(lambda row: row / row.sum() if row.sum() != 0 else row, axis=1)
    commuter_matrix = commuter_matrix.apply(lambda col: (col * nb_employed_people["nb_employed"]).round(), axis=0)
    if __name__ == '__main__':
        print(commuter_matrix)
    return commuter_matrix, distances


def build_commuter_matrix_per_mode(communes, influence_communes, work_communes, commuter_matrix, distances_matrix):
    def set_value(df, row, col, value):
        df.loc[row, col] = value

    commuter_per_mode = pd.DataFrame(index=pd.MultiIndex.from_product([[c.geo_code for c in communes], [1, 2, 3, 4, 5, 6]], names=["geo_code", "mode"]))
    commuter_distances_per_mode = pd.DataFrame(index=pd.MultiIndex.from_product([[c.geo_code for c in communes], [1, 2, 3, 4, 5, 6]], names=["geo_code", "mode"]))

    geo_code_from_wa = {}
    [[geo_code_from_wa.update({wa.id: c.geo_code}) for wa in c.work_areas] for c in communes + influence_communes + work_communes]

    for c in communes:
        flows_prop_by_geo_code_mode, flows_mode = c.flows_prop_by_geo_code_mode, c.flows_prop_by_mode
        for wa_id, flow in commuter_matrix.loc[c.geo_code].items():
            wa_gc = geo_code_from_wa[wa_id]
            if wa_gc in flows_prop_by_geo_code_mode.index.get_level_values(0):
                for mode, flow_prop in flows_prop_by_geo_code_mode.loc[wa_gc, "flow"].items():
                    set_value(commuter_per_mode, (c.geo_code, mode), wa_id, round(flow_prop * flow))
                    set_value(commuter_distances_per_mode, (c.geo_code, mode), wa_id, distances_matrix.loc[c.geo_code, wa_id])
            else:
                for mode, flow_prop in flows_mode["flow"].items():
                    set_value(commuter_per_mode, (c.geo_code, mode), wa_id, round(flow_prop * flow))
                    set_value(commuter_distances_per_mode, (c.geo_code, mode), wa_id, distances_matrix.loc[c.geo_code, wa_id])

    commuter_per_mode.fillna(0, inplace=True)
    commuter_distances_per_mode = commuter_distances_per_mode.where(commuter_per_mode != 0, 1000000)

    return commuter_per_mode, commuter_distances_per_mode


def universal_opportunity_model(communes, work_areas, distances):
    ALPHA = 0.3
    BETA = 0.3

    flows = pd.DataFrame()

    def dist(c, wa):
        return distances.loc[c.geo_code, wa.id]

    def calc_flow(c, wa):
        Oi = c.status["employed"] * (1 - c.workers_within_commune_prop)
        mi = c.jobs_nb
        mj = wa.jobs_nb
        intervening_opportunities = [wa for wa in work_areas if 0 < dist(c, wa) < dist(c, wa)]
        sij = sum([c.jobs_nb - c.status["employed"]*c.workers_within_commune_prop for c in intervening_opportunities])
        flow_ij = Oi * (mi + ALPHA * sij) * mj / (mi + (ALPHA + BETA) * sij) / (mi + (ALPHA + BETA) * sij + mj)
        flows.loc[c.geo_code, wa.id] = flow_ij

    [[calc_flow(c, wa) for wa in work_areas if wa not in c.work_areas] for c in communes]
    return flows


def build_distances_matrix_od(origins, destinations):
    def calc_estimated_dist(coord1, coord2):
        X = np.array(coord1)
        Y = np.array(coord2)
        conv_deg_km = np.array([np.pi / 180 * 6400, np.pi / 180 * 4400])
        crow_fly_dist = abs(np.linalg.norm(np.multiply(X - Y, conv_deg_km)))
        # To estimate dist via road
        # "From crow-fly distances to real distances, or the origin of detours, Heran"
        dist = crow_fly_dist * (1.1 + 0.3 * np.exp(-crow_fly_dist / 20))
        return dist

    def calc_dist(origin, destination):
        dist = calc_estimated_dist(origin.coords, destination.coords)
        distances.loc[origin.geo_code, destination.id] = dist

    distances = pd.DataFrame()
    [[calc_dist(o, d) for d in destinations] for o in origins]
    return distances

