import numpy as np


def create_set_work_area_function(communes, influence_communes, work_communes):
    work_areas = {c.geo_code: c.work_areas for c in communes + influence_communes + work_communes}
    commuter_transport_mode_dict = {c.geo_code: c.flows_prop_by_mode_geo_code for c in communes}
    commuter_missing_transport_mode_dict = {c.geo_code: c.flows_prop_by_geo_code for c in communes}

    def set_work_area_function(geo_code, transport_mode):
        flows_by_transport_mode = commuter_transport_mode_dict[geo_code]
        flows_missing_transport = commuter_missing_transport_mode_dict[geo_code]
        if len(flows_missing_transport) == 0:
            return None
        if int(transport_mode) in flows_by_transport_mode.index.get_level_values(0).to_list():
            geocodes = flows_by_transport_mode.loc[transport_mode].index.tolist()
            probs = flows_by_transport_mode.loc[transport_mode]["flow"]
            geo_code_work = np.random.choice(geocodes, p=probs)
            dest_was = work_areas[geo_code_work]
            dest_was_ids = [wa.id for wa in dest_was]
            wa_probs = np.array([wa.mass for wa in dest_was])
            wa_id = np.random.choice(dest_was_ids, p=wa_probs/wa_probs.sum())
            return wa_id
        else:
            geocodes = flows_missing_transport.index.tolist()
            probs = flows_missing_transport["flow"]
            geo_code_work = np.random.choice(geocodes, p=probs)
            dest_was = work_areas[geo_code_work]
            dest_was_ids = [wa.id for wa in dest_was]
            wa_probs = np.array([wa.mass for wa in dest_was])
            wa_id = np.random.choice(dest_was_ids, p=wa_probs/wa_probs.sum())
            return wa_id

    return set_work_area_function


