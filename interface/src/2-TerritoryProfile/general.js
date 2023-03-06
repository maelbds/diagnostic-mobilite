import React, { Component } from 'react';
import {c_markers, c_gradient_greens, c_missing_data} from '../a-Graphic/Colors';
import {p_size_1, p_size_2, p_size_3, p_size_4, p_size_5} from '../a-Graphic/Layout';
import {formatFigure} from '../f-Utilities/util_func'

import {getLegendMode} from '../b-LeafletMap/leaflet_map';
import {createCommuneBordersLayer} from '../b-LeafletMap/LeafletMapElement/createCommune'
import {createGridLayer} from '../b-LeafletMap/LeafletMapElement/createGrid'
import {createPlacesLayer} from '../b-LeafletMap/LeafletMapElement/createPlaceLayer'

export function getGeneralElements(communes, activity_cluster){
    // Activity Clusters
    let cluster_places = [{level: 0, size: p_size_1, color: c_markers[0], label: "Pôles de proximité", sublabel: "école, médecin, commerce alimentaire"},
                        {level: 1, size: p_size_2, color: c_markers[1], label: "Pôles intermédiaires", sublabel: "restauration, infrastructures sportives ou culturelles, commerces et services" },
                        {level: 2, size: p_size_3, color: c_markers[2], label: "Pôles complets", sublabel: "tous commerces et services"}]
    let places_layer = []

    for (let e_p of cluster_places){
      let places_type = activity_cluster.filter((p) => p.level==e_p.level)
      let places_coords = places_type.map((a) => a.coords)
      let places_labels = places_type.map((a) => a.name)
      places_layer.push(createPlacesLayer(places_coords, e_p.size/2, e_p.color, places_labels))
    }

    // GriddedPop
    let gridded_population = [].concat(...communes.map((c)=>c.gridded_population));
    let gridded_pop_coords = gridded_population.map((c) => c.coords);
    let gridded_pop_masses = gridded_population.map((c) => c.population);
    let gridded_pop_labels = gridded_population.map((c) => formatFigure(c.population) + " hab");

    var legend_values = gridded_pop_masses
    var missing_data = false

    let mode = "ckmeans"
    let legend_label = "Population au carreau"
    let legend_unit = "(hab)"
    let colors = c_gradient_greens

    let sources = ["gridded_pop", "bpe"]

    let communes_layer = createCommuneBordersLayer(communes);
    let gridded_incomes_layer = createGridLayer(gridded_pop_coords, gridded_pop_masses, gridded_pop_labels, mode, colors);

    let [legend_intervals, legend_colors] = getLegendMode(mode, legend_values, colors)
    let legend = [
      {type: "LegendLabel", params: {label: legend_label, unit: legend_unit}},
      {type: "LegendValues", params: {intervals: legend_intervals, colors: legend_colors, missing_data: missing_data}},
      {type: "LegendSpace", params: {}}
    ]
    cluster_places.map((h_p)=> legend.push({type: "LegendPlace", params: {label: h_p.label, color: h_p.color, size: h_p.size+2, subtitle: h_p.sublabel}}))

    let layer_to_fit = communes_layer
    let layers = [communes_layer, gridded_incomes_layer].concat(places_layer.reverse())

    return {layer_to_fit, layers, legend, sources}
}
