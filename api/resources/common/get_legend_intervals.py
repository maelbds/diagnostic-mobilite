import os
import json


def get_legend_intervals(name, mesh, year=None):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    with open('legend_intervals.json') as f:
        all_legend_intervals = json.load(f)

    if year is None:
        return all_legend_intervals[name][mesh]
    else:
        return all_legend_intervals[name][mesh][year]


if __name__ == '__main__':
    print(get_legend_intervals("pop_status", "com"))

