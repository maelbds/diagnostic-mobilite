import pandas as pd
import numpy as np


def analysis(persons, travels, name, save_to_csv=True, light=False, emp=False):
    print("----- ANALYSE " + name + " -----", end='\n\n')
    travels_with_persons = pd.merge(travels, persons, on="id_ind")
    # print(travels_with_persons)

    total_pop = round(persons["w_ind"].sum())
    total_pop_5 = round(persons[persons["age"] > 4]["w_ind"].sum())
    if "immo_lun" in persons.columns:
        total_pop_immo = (persons["immo_lun"] * persons["w_ind"]).sum() + \
                         (persons["immo_mar"] * persons["w_ind"]).sum() + \
                         (persons["immo_mer"] * persons["w_ind"]).sum() + \
                         (persons["immo_jeu"] * persons["w_ind"]).sum() + \
                         (persons["immo_ven"] * persons["w_ind"]).sum()
        immo_rate = total_pop_immo / total_pop / 5
        total_pop_mobile = total_pop * (1 - immo_rate)
    else:
        total_pop_mobile = round(travels_with_persons.drop_duplicates(subset="id_ind")["w_ind"].sum())

    print(f"Population totale : {total_pop:,} "
          f"\nPopulation de +5ans : {total_pop_5:,}"
          f"\nPopulation mobile : {total_pop_mobile:,}, soit {round((1 - total_pop_mobile / total_pop) * 100, 1)}% personnes immobiles",
          end='\n\n')

    total_travels = round(travels_with_persons["w_trav"].sum())
    total_distance = round((travels_with_persons["w_trav"] * travels_with_persons["distance"]).sum())
    print(f"Nombre total de trajets : {total_travels:,}  "
          f"\n - soit {round(total_travels / total_pop, 2)}/pers"
          f"\n - soit {round(total_travels / total_pop_mobile, 2)}/pers mobile", end='\n\n')

    print(f"Distance totale des trajets : {total_distance:,}  "
          f"\n - soit {round(total_distance / total_pop, 2)}km/pers"
          f"\n - soit {round(total_distance / total_pop_mobile, 2)}km/pers mobile", end='\n\n')

    print("-- MODES --")
    modes_nb = (travels_with_persons.groupby("mode_name_fr")["w_trav"].sum() / 1e3).round(2)
    modes_dist = travels_with_persons.groupby("mode_name_fr") \
        .apply(lambda df: round((df["w_trav"] * df["distance"]).sum() / 1e3, 1))
    modes_nb_pers = travels_with_persons.groupby("mode_name_fr") \
        .apply(lambda df: round(df["w_trav"].sum() / total_pop, 2))
    modes_dist_pers = travels_with_persons.groupby("mode_name_fr") \
        .apply(lambda df: round((df["w_trav"] * df["distance"]).sum() / total_pop, 2))
    modes_significance = travels_with_persons.groupby("mode_name_fr") \
        .apply(lambda df: df["id_ind"].drop_duplicates().count())
    modes = pd.DataFrame({#"nombre - milliers": modes_nb,
                          "nombre/pers": modes_nb_pers,
                          "nombre - %": (modes_nb / modes_nb.sum() * 100).round(1),
                          #"distance - milliers km": modes_dist,
                          "distance/pers": modes_dist_pers,
                          "distance - %": (modes_dist / modes_dist.sum() * 100).round(1),
                          "effectif": modes_significance})
    print(modes, end='\n\n')

    if save_to_csv:
        modes.to_csv("analysis_data/" + name + "_modes.csv")

    print("-- MOTIFS --")
    reasons_nb = (travels_with_persons.groupby("reason_name_fr")["w_trav"].sum() / 1e3).round(2)
    resons_dist = travels_with_persons.groupby("reason_name_fr") \
        .apply(lambda df: round((df["w_trav"] * df["distance"]).sum() / 1e3, 1))
    resons_nb_pers = travels_with_persons.groupby("reason_name_fr") \
        .apply(lambda df: round(df["w_trav"].sum() / total_pop, 2))
    resons_dist_pers = travels_with_persons.groupby("reason_name_fr") \
        .apply(lambda df: round((df["w_trav"] * df["distance"]).sum() / total_pop, 2))
    reasons_significance = travels_with_persons.groupby("reason_name_fr") \
        .apply(lambda df: df["id_ind"].drop_duplicates().count())
    reasons = pd.DataFrame({#"nombre - milliers": reasons_nb,
                            "nombre/pers": resons_nb_pers,
                            "nombre - %": (reasons_nb / reasons_nb.sum() * 100).round(1),
                            #"distance - milliers km": resons_dist,
                            "distance/pers": resons_dist_pers,
                            "distance - %": (resons_dist / resons_dist.sum() * 100).round(1),
                            "effectif": reasons_significance})
    print(reasons, end='\n\n')
    if save_to_csv:
        reasons.to_csv("analysis_data/" + name + "_motifs.csv")

    if not light:

        print(" - répartition par classes de distance")

        def by_dist_reason(travels, reason):
            reason_travels = travels[travels["reason_name_fr"] == reason]
            reason_travels_by_dist10 = reason_travels["w_trav"].groupby(reason_travels["distance_class_10"]).sum()
            reason_travels_by_dist10 = (reason_travels_by_dist10 / reason_travels_by_dist10.sum() * 100).round(
                2).rename(reason + " par classes de 10km").iloc[:9]
            print(reason_travels_by_dist10)
            if save_to_csv:
                reason_travels_by_dist10.to_csv("analysis_data/" + name + "_motifs_dist_10_" + reason[11:] + ".csv")

            reason_travels_by_dist1 = reason_travels["w_trav"].groupby(reason_travels["distance_class_1"]).sum()
            reason_travels_by_dist1 = (reason_travels_by_dist1 / reason_travels_by_dist1.sum() * 100).round(2).rename(
                reason + " par classes de 1km (détail trajets <10km)").iloc[:10]
            print(reason_travels_by_dist1, end='\n\n')
            if save_to_csv:
                reason_travels_by_dist1.to_csv("analysis_data/" + name + "_motifs_dist_1_" + reason[11:] + ".csv")

        travels_with_persons["distance_class_10"] = np.floor(travels_with_persons["distance"] / 10) * 10
        travels_with_persons["distance_class_1"] = np.floor(travels_with_persons["distance"])
        by_dist_reason(travels_with_persons, "domicile ↔ achats")
        by_dist_reason(travels_with_persons, "domicile ↔ loisirs")
        # by_dist_reason(travels_with_persons, "domicile ↔ visites")
        # by_dist_reason(travels_with_persons, "domicile ↔ affaires personnelles")

        print("-- ANALYSE TRAJETS A PIED")
        walk_travels = travels_with_persons[travels_with_persons["mode_name_fr"] == "à pied"]
        walk_travels["dist_cat"] = np.floor(walk_travels["distance"] / 0.5) * 0.5

        print("répartition par classes de distance (500m) - en nombre")
        walk_travels_by_dist = walk_travels[["dist_cat", "w_trav"]].groupby(by="dist_cat").sum().apply(
            lambda col: round(col / col.sum() * 100, 1) if col.sum() != 0 else col).iloc[:10]
        print(walk_travels_by_dist)
        if save_to_csv:
            walk_travels_by_dist.to_csv("analysis_data/" + name + "_walk_dist.csv")

        print("répartition par profil")
        walk_travels_by_status = walk_travels[["status", "w_trav"]].groupby(by="status").sum().apply(
            lambda col: round(col / col.sum() * 100, 1) if col.sum() != 0 else col)
        print(walk_travels_by_status)
        if save_to_csv:
            walk_travels_by_status.to_csv("analysis_data/" + name + "_walk_status.csv")

        print("répartition par motif")
        walk_travels_by_reason = walk_travels[["reason_name_fr", "w_trav"]].groupby(by="reason_name_fr").sum().apply(
            lambda col: round(col / col.sum() * 100, 1) if col.sum() != 0 else col)
        print(walk_travels_by_reason)
        if save_to_csv:
            walk_travels_by_reason.to_csv("analysis_data/" + name + "_walk_reason.csv")

        print("répartition par profil & motif")
        walk_travels_by_status_reason = walk_travels[["reason_name_fr", "status", "w_trav"]].groupby(
            by=["status", "reason_name_fr"]).sum().apply(
            lambda col: round(col / col.sum() * 100, 1) if col.sum() != 0 else col).sort_values(by="w_trav",
                                                                                                ascending=False).iloc[
                                        :15]
        print(walk_travels_by_status_reason)
        if save_to_csv:
            walk_travels_by_status_reason.to_csv("analysis_data/" + name + "_walk_status_reason.csv")

    return {"nb/pers": round(total_travels / total_pop, 2),
            "modes": modes[["nombre/pers", "nombre - %", "effectif"]],
            "reasons": reasons[["nombre/pers", "nombre - %", "effectif"]]}
