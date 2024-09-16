import pandas as pd
import numpy as np
from pprint import pprint


def general_uo_model(ori_areas, des_areas, distances, ALPHA = 0.3, BETA = 0.3):
    """
    From Liu & Yan 2020
    """
    ori_ids = ori_areas["id"]
    ni = len(ori_ids)
    ori_masses = np.array([1] * ni)  # 1 to prevent from division by 0 during computation

    des_ids = des_areas["id"]
    nj = len(des_ids)
    des_masses = des_areas["mass"]

    matrix_mi = pd.DataFrame(np.array([ori_masses] * nj).T)
    matrix_mj = pd.DataFrame(np.array([des_masses] * ni))

    matrix_dij = distances.loc[ori_ids, des_ids]

    def get_sijs(i):
        dists_from_i = matrix_dij.iloc[i, :].to_list()
        j_areas_from_i = pd.DataFrame({"id": des_ids, "mass": des_masses, "dists_from_i": dists_from_i})
        j_areas_from_i = j_areas_from_i.sort_values(by="dists_from_i")
        j_areas_from_i["io_masses"] = j_areas_from_i["mass"].cumsum().shift(fill_value=0)
        j_areas_from_i = j_areas_from_i.sort_index()
        io_masses_i = j_areas_from_i["io_masses"].to_list()
        return io_masses_i
    matrix_sij = pd.DataFrame([get_sijs(i) for i in range(ni)])

    matrix_aij = (matrix_mi + ALPHA * matrix_sij).mul(matrix_mj)
    matrix_bij = (matrix_mi + (ALPHA + BETA) * matrix_sij)
    matrix_cij = (matrix_mi + (ALPHA + BETA) * matrix_sij + matrix_mj)

    matrix_pij = matrix_aij.div(matrix_bij.mul(matrix_cij))
    matrix_pij = matrix_pij.apply(lambda x: x/sum(x), axis=1)
    matrix_pij = matrix_pij.set_axis(labels=ori_ids.tolist(), axis=0)
    matrix_pij = matrix_pij.set_axis(labels=des_ids.tolist(), axis=1)

    """ former computation : longer
    flows = pd.DataFrame()

    def dist(ori_id, des_id):
        return distances.loc[ori_id, des_id]

    def calc_prob(ori_id, des_id, des_mass):
        mi = 1
        mj = des_mass if des_mass != 0 else 1
        intervening_opportunities_masses = [d_mass for d_mass, d_id in zip(des_areas["mass"], des_areas["id"])
                                            if 0 < dist(ori_id, d_id) < dist(ori_id, des_id)]
        sij = sum([iom if iom != 0 else 1 for iom in intervening_opportunities_masses])
        flow_ij = (mi + ALPHA * sij) * mj / (mi + (ALPHA + BETA) * sij) / (mi + (ALPHA + BETA) * sij + mj)
        flows.loc[ori_id, des_id] = flow_ij

    [[calc_prob(ori_id, des_id, des_mass) for des_id, des_mass in zip(des_areas["id"], des_areas["mass"]) if des_id != ori_id]
     for ori_id in ori_areas["id"]]

    flows = flows.apply(lambda x: x/sum(x), axis=1)
    print(flows)"""

    return matrix_pij
