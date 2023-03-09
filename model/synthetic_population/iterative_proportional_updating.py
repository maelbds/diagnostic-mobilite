"""
Implementation of Iterative Proportional Updating (IPU)

https://hal.archives-ouvertes.fr/file/index/docid/725531/filename/PopGen.pdf
https://hal.archives-ouvertes.fr/hal-03196270/document
Ye et al 2019
"""
import pprint
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
    ipu_weights = []

    delta_max = epsilon + 1

    counter = 0
    while delta_max > epsilon and counter < max_iterations:
        if __name__ == '__main__':
            print(counter)
        counter += 1
        for j in range(len(marginals)):
            if weighted_sum[j] != 0:
                weights = [weight*marginals[j]/weighted_sum[j] if occurence != 0 else weight for (occurence, weight)
                           in zip(occurences[:, j], weights)]
            else:
                weights = [0 if occurence != 0 else weight for (occurence, weight)
                           in zip(occurences[:, j], weights)]
            weighted_sum = np.dot(occurences.transpose(), weights)
        deltas = [abs(ws - m) / m if m != 0 else ws for ws, m in zip(weighted_sum, marginals)]

        delta_max = max(deltas)
        # pprint.pprint(deltas)
        if __name__ == '__main__':
            print(delta_max)
        ipu_weights = weights
        """
        delta = sum(deltas)/len(deltas)
        d = abs(delta - d_prev)
        if delta < delta_min:
            delta_min = delta
            ipu_weights = weights
        """
    return ipu_weights


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



