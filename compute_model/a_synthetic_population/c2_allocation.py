import math
import random


def stochastic_rounding(weights):
    """
    Stochastic rounding (Gupta et al., 2015)
    :param weights: associated weights (List)
    :return: integer weights (List)
    """
    if sum(weights) > 0:
        int_weights = [math.trunc(w) if random.random() < 1 - (w - math.trunc(w)) else math.trunc(w) + 1 for w in weights]
    else:
        int_weights = weights
    return int_weights


if __name__ == '__main__':
    print(stochastic_rounding([1.2, 0.3, 3.8, 0.25, 0.4, 0.99]))

