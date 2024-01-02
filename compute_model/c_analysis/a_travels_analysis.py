import pandas as pd


def analyse_travels(travels):
    travels["number"] = 1

    print("-- MODES --")
    modes_nb = (travels.groupby("mode_name_fr")["w_trav"].sum() / 1e3).round(2)
    modes_dist = travels.groupby("mode_name_fr") \
        .apply(lambda df: round((df["w_trav"] * df["distance"]).sum() / 1e3, 1))
    modes_significance = travels.groupby("mode_name_fr") \
        .apply(lambda df: df["id_ind"].drop_duplicates().count())
    modes = pd.DataFrame({"nombre - %": (modes_nb / modes_nb.sum() * 100).round(1),
                          "distance - %": (modes_dist / modes_dist.sum() * 100).round(1),
                          "effectif": modes_significance})
    print(modes, end='\n\n')

    print("-- DISTANCE --")
    total_dist = (travels["w_trav"] * travels["distance"]).sum()
    total_pop = len(travels["id_ind"].drop_duplicates())
    print(f"Distance moyenne (km/pers) {round(total_dist/total_pop)}")

    to_db = pd.DataFrame({
        "nb_car": modes.loc["voiture", "nombre - %"],
        "nb_car_pass": modes.loc["voiture passager", "nombre - %"],
        "nb_pt": modes.loc["transport en commun", "nombre - %"],
        "nb_bike": modes.loc["vélo", "nombre - %"],
        "nb_pedestrian": modes.loc["à pied", "nombre - %"],
        "dist_car": modes.loc["voiture", "distance - %"],
        "dist_car_pass": modes.loc["voiture passager", "distance - %"],
        "dist_pt": modes.loc["transport en commun", "distance - %"],
        "dist_bike": modes.loc["vélo", "distance - %"],
        "dist_pedestrian": modes.loc["à pied", "distance - %"],
        "avg_dist": round(total_dist/total_pop),
    }, index=[0])

    return to_db
