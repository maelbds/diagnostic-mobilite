

def set_matching_attributes(syn_pop, dist_matrix_ra_stops):
    # ---- AGE
    def compute_age_cat(age):
        if age < 2:
            return 0
        elif 2 <= age <= 5:
            return 1
        elif 6 <= age <= 10:
            return 2
        elif 11 <= age <= 14:
            return 3
        elif 15 <= age <= 17:
            return 4
        elif 18 <= age <= 24:
            return 5
        else:
            return age // 5 + 1

    syn_pop["age_cat"] = syn_pop["age"].apply(lambda a: compute_age_cat(a))

    # ---- PUBLIC TRANSPORT DISTANCE
    def compute_dist_pt(id):
        if len(dist_matrix_ra_stops.index) == 0:
            return 1000
        min_dist = dist_matrix_ra_stops.loc[id].min()
        if min_dist < 0.3:
            return 0
        elif min_dist < 0.6:
            return 300
        elif min_dist < 1:
            return 600
        else:
            return 1000
    syn_pop["dist_pt"] = syn_pop["ra_id"].apply(lambda id: compute_dist_pt(id))

    # ---- some family composition ratios
    syn_pop["child/adult"] = syn_pop["nb_child"] / (syn_pop["nb_pers"] - syn_pop["nb_child"])
    syn_pop["child/adult_is1+"] = syn_pop["child/adult"].apply(lambda x: 0 if x < 1 else 1)
    syn_pop["child/adult"] = syn_pop["child/adult"].round(2)

    syn_pop["car/adult"] = syn_pop.apply(
        lambda row: row["nb_car"] / (row["nb_pers"] - row["nb_child"]) if row["nb_pers"] > row["nb_child"] else 0,
        axis=1)
    syn_pop["car/adult_is1+"] = syn_pop["car/adult"].apply(lambda x: min(round(x * 2) / 2, 1))
    syn_pop["car/adult"] = syn_pop["car/adult"].round(2)

    return syn_pop


def adapt_work_distance(dist):
    return min(dist, 400)**(1/4)

