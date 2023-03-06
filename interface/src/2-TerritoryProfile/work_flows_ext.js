import React, { Component } from 'react';
import {c_gradient_reds} from '../a-Graphic/Colors';
import {formatFigure, titleCase} from '../f-Utilities/util_func'

import {getLegendMode} from '../b-LeafletMap/leaflet_map';
import {createFlowsLayer} from '../b-LeafletMap/LeafletMapElement/createFlow'
import {createCommuneBordersLayer} from '../b-LeafletMap/LeafletMapElement/createCommune'

const L = window.L;


var f_limit = 20;


export function getWorkFlowsExtElements(communes, influence_communes, work_communes, limit_flows_nb, selectCommuneExtLimit){

  // dictionnaries geocode to name & geocode to coords for all communes
  var communes_geo_codes_to_coords = {};
  communes.concat(influence_communes).concat(work_communes).map((c) => communes_geo_codes_to_coords[c.geo_code] = c.center)
  var communes_geo_codes_to_names = {};
  communes.concat(influence_communes).concat(work_communes).map((c) => communes_geo_codes_to_names[c.geo_code] = c.name)

  // all flows
  let flows = []
  communes.forEach((c, i) => {
    Object.keys(c.flows_home_work_workers).filter((c_geo)=> c.flows_home_work_workers[c_geo]["flow"]>f_limit)
                                          .filter((c_geo)=> !communes.map((c)=>c.geo_code).includes(c_geo)).forEach((c_geo) => {
      flows.push({
        coords: [c.center, c.flows_home_work_workers[c_geo]["coords"]],
        mass: c.flows_home_work_workers[c_geo]["flow"],
        label: titleCase(c.flows_home_work_workers[c_geo]["name"]) + " → " + c.name + " : " + formatFigure(c.flows_home_work_workers[c_geo]["flow"]) + " navetteurs"
      })
    })
  });

  flows = flows.sort(((a,b)=> b.mass - a.mass))
  flows = flows.slice(0, limit_flows_nb)

  let flows_coords = flows.map((f) => f.coords)
  let flows_masses = flows.map((f) => f.mass)
  let flows_labels = flows.map((f) => f.label)


  let mode = "ckmeans"
  let legend_label = "Flux principaux"
  let legend_unit = "(nombre de navetteurs)"
  let colors = c_gradient_reds
  let sources = ["mobpro"]

  let legend_values = flows_masses

  // --- create layers
  let communes_layer = createCommuneBordersLayer(communes)
  let flows_layer = createFlowsLayer(flows_coords, flows_masses, flows_labels, mode, colors);

  let [legend_intervals, legend_colors] = getLegendMode(mode, legend_values, colors)
  let legend = [
    {type: "LegendDescription", params: {desc: "Vue d'ensemble des navetteurs qui n'habitent pas le territoire mais y travaillent."}},
    {type: "LegendCursor", params: {min: 25,
                                    max: 200,
                                    step: 25,
                                    id: "flows_ext",
                                    value: limit_flows_nb,
                                    cursorFunction: selectCommuneExtLimit}},
    {type: "LegendDescription", params: {desc: "Seuls les " + limit_flows_nb + " flux les plus importants sont affichés (de plus de 20 navetteurs)."}},
    {type: "LegendSpace", params: {}},
    {type: "LegendLabel", params: {label: legend_label, unit: legend_unit}},
    {type: "LegendValuesFlows", params: {intervals: legend_intervals, colors: legend_colors}},
  ]

  let layer_to_fit = communes_layer
  let layers = [communes_layer, flows_layer]

  return {layer_to_fit, layers, legend, sources}
}
