import pandas as pd

from api.resources.common.log_stats import log_stats
from api.resources.mobility.utilities.get_travels_sources import get_travels_sources
from api.resources.mobility.utilities.get_travels import get_travels

from flask_restful import Resource

from api.resources.common.log_message import message_request
from api.resources.common.schema_request import context_get_request
from api.resources.mobility.utilities.significance_threshold import SIGNIFICANCE_THRESHOLD


def get_focus_home_not_work(geo_codes):
    travels = get_travels(geo_codes)

    mask_home_not_work = travels["reason_name_fr"].isin(["domicile ↔ études", "domicile ↔ achats",
                                                     "domicile ↔ accompagnement", "domicile ↔ loisirs",
                                                     "domicile ↔ visites", "domicile ↔ affaires personnelles"])
    travels = travels.loc[mask_home_not_work]

    significance = travels["id_ind"].drop_duplicates().count()

    if len(travels) == 0 or significance < SIGNIFICANCE_THRESHOLD:
        return {
            "modes": None,
            "dist_class": None,
            "total_nb": "--",
            "total_dist": "--",
            "total_dist_pers": "--",
            "sources": []
        }

    total_nb = travels["w_trav"].sum().round()
    total_dist = (travels["w_trav"] * travels["distance"]).sum().round()
    total_persons = travels[["id_ind", "w_ind"]].drop_duplicates(subset=["id_ind"])["w_ind"].sum()
    total_dist_pers = round(total_dist / total_persons)

    # modes repartition
    modes_nb = travels.groupby("mode_name_fr")["w_trav"].sum().round()
    modes_dist = travels.groupby("mode_name_fr") \
        .apply(lambda df: (df["w_trav"] * df["distance"]).sum().round())
    modes_significance = travels.groupby("mode_name_fr") \
        .apply(lambda df: df["id_ind"].drop_duplicates().count())

    modes = pd.DataFrame({
        "number": modes_nb,
        "distance": modes_dist,
        "id": modes_significance
    }).reset_index()

    mask_significance = modes["id"] < SIGNIFICANCE_THRESHOLD
    modes.loc[mask_significance, "mode_name_fr"] = "imprécis"

    modes = modes.groupby("mode_name_fr").sum()

    # distance class repartition
    class_dist_thresholds = [1, 5, 7, 10, 20]
    dict_class_dist = {}
    for i in range(len(class_dist_thresholds)-1):
        from_km = class_dist_thresholds[i]
        to_km = class_dist_thresholds[i+1]
        legend = f"de {from_km} à {to_km} km"
        travels.loc[(from_km <= travels["distance"]) &
                    (travels["distance"] < to_km), "class_dist"] = legend
        dict_class_dist[legend] = i + 1

    first_class_t = class_dist_thresholds[0]
    first_class_l = f"moins de {first_class_t} km"
    travels.loc[(travels["distance"] < first_class_t), "class_dist"] = first_class_l
    dict_class_dist[first_class_l] = 0

    last_class_t = class_dist_thresholds[-1]
    last_class_l = f"plus de {last_class_t} km"
    travels.loc[(last_class_t <= travels["distance"]), "class_dist"] = last_class_l
    dict_class_dist[last_class_l] = len(class_dist_thresholds) + 1

    dict_class_dist["imprécis"] = len(class_dist_thresholds) + 2

    dist_class_nb = travels.groupby("class_dist")["w_trav"].sum().round()
    dist_class_dist = travels.groupby("class_dist") \
        .apply(lambda df: (df["w_trav"] * df["distance"]).sum().round())
    dist_class_significance = travels.groupby("class_dist") \
        .apply(lambda df: df["id_ind"].drop_duplicates().count())

    dist_class = pd.DataFrame({
        "number": dist_class_nb,
        "distance": dist_class_dist,
        "id": dist_class_significance
    }).reset_index()

    mask_significance = dist_class["id"] < SIGNIFICANCE_THRESHOLD
    dist_class.loc[mask_significance, "class_dist"] = "imprécis"

    dist_class = dist_class.groupby("class_dist").sum()

    return {
        "modes": modes.to_dict(),
        "dist_class": {
            "dict": dict_class_dist,
            "number": dist_class["number"].to_dict(),
            "distance": dist_class["distance"].to_dict(),
            "id": dist_class["id"].to_dict(),
        },
        "total_nb": total_nb,
        "total_dist": total_dist,
        "total_dist_pers": total_dist_pers,
        "references": {
            "france": {}
        },
        "sources": get_travels_sources(geo_codes),
    }


class FocusHomeNotWork(Resource):
    def get(self):
        perimeter = context_get_request.parse()
        geo_codes = perimeter.geo_codes

        log_stats("focus_home_not_work", geo_codes, None, None)
        message_request("focus_home_not_work", geo_codes)
        return get_focus_home_not_work(geo_codes)


if __name__ == '__main__':
    print("go")
    print(get_focus_home_not_work(["79270"]))
