"""
Implementation of Iterative Proportional Updating (IPU)

https://hal.archives-ouvertes.fr/file/index/docid/725531/filename/PopGen.pdf
https://hal.archives-ouvertes.fr/hal-03196270/document
Ye et al 2019
"""
import time
import pandas as pd
import numpy as np


def iterative_proportional_updating(occurences, marginals, weights=None, epsilon=0.03, max_iterations=50):
    # initialization of weights
    if weights is None:
        df_len = occurences.shape[0]
        weights = df_len*[1]

    # initialization of deltas (provides a goodness of fit result) & weighted sum
    weighted_sum = np.dot(occurences.transpose(), weights)
    deltas = [abs(ws-m)/m if m != 0 else ws for ws, m in zip(weighted_sum, marginals)]

    delta = sum(deltas)/len(deltas)
    delta_min = delta
    d = epsilon + 1

    delta_max = epsilon + 1
    delta_max_prec = delta_max + 1

    counter = 0
    while epsilon < delta_max and counter < max_iterations:
        if __name__ == '__main__':
            print(counter)

        counter += 1
        delta_max_prec = delta_max

        for j in range(len(marginals)):
            if weighted_sum[j] != 0:
                coef = marginals[j]/weighted_sum[j]
                adjustment = [coef if occurence != 0 else 1 for occurence in occurences[:, j]]
                weights = np.multiply(weights, adjustment)
            else:
                adjustment = [0 if occurence != 0 else 1 for occurence in occurences[:, j]]
                weights = np.multiply(weights, adjustment)
            weighted_sum = np.dot(occurences.transpose(), weights)
        deltas = [abs(ws - m) / m if m != 0 else ws for ws, m in zip(weighted_sum, marginals)]

        delta_max = max(deltas)
        # pprint.pprint(deltas)
        if __name__ == '__main__':
            print(delta_max)

        """
        delta = sum(deltas)/len(deltas)
        d = abs(delta - d_prev)
        if delta < delta_min:
            delta_min = delta
            ipu_weights = weights
        """
    return weights


if __name__ == '__main__':
    """
    Example from Table 1
    https://www.researchgate.net/publication/228963837_Methodology_to_match_distributions_of_both_household_and_person_attributes_in_generation_of_synthetic_populations
    """
    o = pd.DataFrame()
    o["1"] = np.array([1, 1, 1, 0, 0, 0, 0, 0])
    o["2"] = np.array([0, 0, 0, 1, 1, 1, 1, 1])
    o["3"] = np.array([1, 1, 2, 1, 0, 1, 2, 1])
    o["4"] = np.array([1, 0, 1, 0, 2, 1, 1, 1])
    o["5"] = np.array([1, 1, 0, 2, 1, 0, 2, 0])
    o = o.to_numpy()

    w = [1, 1, 2, 1, 1, 3, 1, 1]
    m = np.array([35, 65, 91, 65, 104])

    ipu_w = iterative_proportional_updating(o, m)
    print(ipu_w)



