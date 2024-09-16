import pandas as pd
import os
from compute_model.database_connection.db_request import db_request


def get_travels_analysis():
    result = db_request(
        """ SELECT siren, LIBEPCI, nb_car, nb_car_pass, nb_pt, nb_bike, nb_pedestrian, dist_car, dist_car_pass, 
                    dist_pt, dist_bike, dist_pedestrian, avg_dist
            FROM computed_travels_analysis
            LEFT JOIN insee_epci ON computed_travels_analysis.siren = insee_epci.EPCI
        """, {}
    )
    travels_analysis = pd.DataFrame(result, columns=["siren", "name",
                                                     "nb_car", "nb_car_pass", "nb_pt", "nb_bike", "nb_pedestrian",
                                                     "dist_car", "dist_car_pass", "dist_pt", "dist_bike", "dist_pedestrian",
                                                     "avg_dist"])

    indicators = ["nb_car", "nb_car_pass", "nb_pt", "nb_bike", "nb_pedestrian",
                  "dist_car", "dist_car_pass", "dist_pt", "dist_bike", "dist_pedestrian",
                  "avg_dist"]

    print(travels_analysis)

    for indicator in indicators:
        print(f" --- {indicator}")
        print(" - min")
        print(travels_analysis.loc[travels_analysis[indicator].idxmin()])
        print(" - max")
        print(travels_analysis.loc[travels_analysis[indicator].idxmax()])

    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    travels_analysis.drop(columns=["name"], inplace=True)
    travels_analysis.to_csv("data/travels_analysis.csv", index=False)


if __name__ == '__main__':
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.width', 200)
    get_travels_analysis()
