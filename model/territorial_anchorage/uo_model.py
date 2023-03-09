import pandas as pd


def general_uo_model(ori_areas, des_areas, distances, ALPHA = 0.3, BETA = 0.3):
    """
    Liu & Yan 2020
    :param ori_areas:
    :param des_areas:
    :param distances:
    :return:
    """

    flows = pd.DataFrame()

    def dist(o_a, d_a):

        return distances.loc[o_a.id, d_a.id]

    def calc_prob(o_a, d_a):
        mi = 1
        mj = d_a.mass if d_a.mass != 0 else 1
        intervening_opportunities = [des_a for des_a in des_areas if 0 < dist(o_a, des_a) < dist(o_a, d_a)]
        sij = sum([io.mass if io.mass != 0 else 1 for io in intervening_opportunities])
        flow_ij = (mi + ALPHA * sij) * mj / (mi + (ALPHA + BETA) * sij) / (mi + (ALPHA + BETA) * sij + mj)
        flows.loc[o_a.id, d_a.id] = flow_ij

    [[calc_prob(o_a, d_a) for d_a in des_areas if d_a != o_a] for o_a in ori_areas]

    flows = flows.apply(lambda x: x/sum(x), axis=1)
    return flows
