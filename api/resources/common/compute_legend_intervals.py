import json
import os

from api.resources.offer.critair import compute_legend_intervals as li_critair
from api.resources.offer.households_motorisation import compute_legend_intervals as li_hh_motorisation
from api.resources.territory.pop_csp import compute_legend_intervals as li_pop_csp
from api.resources.territory.pop_status import compute_legend_intervals as li_pop_status
from api.resources.territory.population import compute_legend_intervals as li_population


def save_legend_intervals():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    all_legend_intervals = {
        "pop_csp": li_pop_csp(),
        "pop_status": li_pop_status(),
        "critair": li_critair(),
        "hh_motorisation": li_hh_motorisation(),
        "population": li_population(),
    }

    with open('legend_intervals.json', 'w') as f:
        json.dump(all_legend_intervals, f)


if __name__ == '__main__':
    save_legend_intervals()
