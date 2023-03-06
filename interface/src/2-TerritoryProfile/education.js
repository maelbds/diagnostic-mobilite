import React, { Component } from 'react';
import {c_markers, c_gradient_greens, c_missing_data} from '../a-Graphic/Colors';
import {p_size_1, p_size_2, p_size_3, p_size_4, p_size_5} from '../a-Graphic/Layout';
import {formatFigure} from '../f-Utilities/util_func'

import {getLegendMode} from '../b-LeafletMap/leaflet_map';
import {createCommunesMassLayer, createCommunesLayer} from '../b-LeafletMap/LeafletMapElement/createCommune'
import {createPlacesLayer} from '../b-LeafletMap/LeafletMapElement/createPlaceLayer'

export function getEducationElements(communes, places){
    // Education Places
    let education_places = [{type: "pre school", size: p_size_1, color: c_markers[0], label: "École maternelle"},
                        {type: "primary school", size: p_size_2, color: c_markers[1], label: "École primaire"},
                        {type: "secondary school", size: p_size_3, color: c_markers[2], label: "Collège"},
                        {type: "high school", size: p_size_4, color: c_markers[3], label: "Lycée"},
                        {type: "university", size: p_size_5, color: c_markers[4], label: "Université"}]
    let education_places_layer = []

    for (let e_p of education_places){
      let school_type = places.filter((p) => [e_p.type].includes(p.type.toLowerCase()))
      let school_coords = school_type.map((a) => a.coords)
      let school_labels = school_type.map((a) => a.name)
      education_places_layer.push(createPlacesLayer(school_coords, e_p.size/2, e_p.color, school_labels))
    }

    // Communes
    let communes_wd = communes.filter((c) => c.status.scholars_11_14 + c.status.scholars_15_17 + c.status.scholars_18 + c.status.scholars_2_5 + c.status.scholars_6_10 != null)

    let communes_masses = communes_wd.map((c) => c.status.scholars_11_14 + c.status.scholars_15_17 + c.status.scholars_18 + c.status.scholars_2_5 + c.status.scholars_6_10);
    let communes_labels = communes_wd.map((c) => c.name + " - " + formatFigure(c.status.scholars_11_14 + c.status.scholars_15_17 + c.status.scholars_18 + c.status.scholars_2_5 + c.status.scholars_6_10) + " élèves");

    let communes_nd = communes.filter((c) => c.status.scholars_11_14 + c.status.scholars_15_17 + c.status.scholars_18 + c.status.scholars_2_5 + c.status.scholars_6_10 == null)
    let communes_nd_labels = communes_nd.map((c) => c.name);

    let mode = "ckmeans"
    let legend_label = "Nombre d'élèves"
    let legend_unit = ""
    let colors = c_gradient_greens
    let sources = ["dossier_complet", "education_data_gouv"]

    let legend_values = communes_masses
    let missing_data = communes_nd.length > 0

    // --- create layers
    let communes_layer = createCommunesMassLayer(communes_wd, communes_masses, communes_labels, mode, colors);
    let communes_layer_nd = createCommunesLayer(communes_nd, communes_nd_labels, c_missing_data);

    let [legend_intervals, legend_colors] = getLegendMode(mode, legend_values, colors)
    let legend = [
      {type: "LegendLabel", params: {label: legend_label, unit: legend_unit}},
      {type: "LegendValues", params: {intervals: legend_intervals, colors: legend_colors, missing_data: missing_data}},
      {type: "LegendSpace", params: {}}
    ]
    education_places.map((h_p)=> legend.push({type: "LegendPlace", params: {label: h_p.label, color: h_p.color, size: h_p.size+2}}))

    let layer_to_fit = communes_layer.addLayer(communes_layer_nd)
    let layers = [communes_layer, communes_layer_nd].concat(education_places_layer.reverse())

    return {layer_to_fit, layers, legend, sources}
}
