import React, { Component } from 'react';
import {c_gradient_reds, c_light} from '../a-Graphic/Colors';
import {formatFigure} from '../f-Utilities/util_func'

import {managePopup} from '../b-LeafletMap/LeafletMapUtil/managePopup';
import {getLegendMode} from '../b-LeafletMap/leaflet_map';
import {createFlowsLayer} from '../b-LeafletMap/LeafletMapElement/createFlow'

const L = window.L;


var f_limit = 20;



export function getWorkFlowsCommuneElements(communes, influence_communes, work_communes, selected_commune_geocode, selectCommuneIndex){
  var communes_coords = communes.map((c) => c.center);
  var communes_names = communes.map((c) => c.name);

  // dictionnaries geocode to name & geocode to coords for all communes
  var communes_geo_codes_to_coords = {};
  communes.concat(influence_communes).concat(work_communes).map((c) => communes_geo_codes_to_coords[c.geo_code] = c.center)
  var communes_geo_codes_to_names = {};
  communes.concat(influence_communes).concat(work_communes).map((c) => communes_geo_codes_to_names[c.geo_code] = c.name)

  // all flows sorted
  var flows_geocode = communes.map((c) => c.geo_code)
  var flows_coords = communes.map((c) => Object.keys(c.flows_home_work).filter((c_geo)=> c.flows_home_work[c_geo]>f_limit).sort((c_geo1, c_geo2) => c.flows_home_work[c_geo2] - c.flows_home_work[c_geo1]).map((c_geo)=> [c.center, communes_geo_codes_to_coords[c_geo]]))
  var flows_masses = communes.map((c) => Object.keys(c.flows_home_work).filter((c_geo)=> c.flows_home_work[c_geo]>f_limit).sort((c_geo1, c_geo2) => c.flows_home_work[c_geo2] - c.flows_home_work[c_geo1]).map((c_geo)=> c.flows_home_work[c_geo]))
  var flows_labels = communes.map((c) => Object.keys(c.flows_home_work).filter((c_geo)=> c.flows_home_work[c_geo]>f_limit).sort((c_geo1, c_geo2) => c.flows_home_work[c_geo2] - c.flows_home_work[c_geo1]).map((c_geo)=> c.name + " → " + communes_geo_codes_to_names[c_geo]  + " : " + formatFigure(c.flows_home_work[c_geo]) + " navetteurs"))

  // adding internal flows
  communes.forEach((c, i) => {
    let within_flow = parseInt(c.workers_within_commune_prop * c.status.employed)
    if (within_flow >= f_limit){
      flows_coords[i].unshift([c.center, c.center])
      flows_masses[i].unshift(within_flow)
      flows_labels[i].unshift(c.name + " → " + c.name  + " : " + formatFigure(within_flow) + " navetteurs")
    }
  });


  // finding main commune to initialize map
  var flows_masses_sum = communes.map((c) => Object.values(c.flows_home_work).reduce((a, b) => a+b, 0) + c.workers_within_commune_prop * c.status.employed);
  var index_main_commune = flows_masses_sum.indexOf(Math.max(...flows_masses_sum))

  // index of selected flow layer to show
  var selected_flow_layer = selected_commune_geocode == null ? index_main_commune : flows_geocode.indexOf(selected_commune_geocode)


  let mode = "ckmeans"
  let legend_label = "Flux principaux "
  let legend_unit = "(nombre de navetteurs)"
  let colors = c_gradient_reds
  let sources = ["mobpro"]

  let legend_values = flows_masses[selected_flow_layer]

  // --- create layers
  let communes_layer = createClickableCommuneLayer(communes, selectCommuneIndex)
  let flows_layer = createFlowsLayer(flows_coords[selected_flow_layer], flows_masses[selected_flow_layer], flows_labels[selected_flow_layer], mode, colors);

  let [legend_intervals, legend_colors] = getLegendMode(mode, legend_values, colors)
  let legend = [
    {type: "LegendDescription", params: {desc: "Cliquer sur une commune pour afficher les flux domicile → travail relatifs à la population active de celle-ci (de plus de " + f_limit + " navetteurs)."}},
    {type: "LegendSpace", params: {}},
    {type: "LegendLabel", params: {label: legend_label, unit: legend_unit}},
    {type: "LegendValuesFlows", params: {intervals: legend_intervals, colors: legend_colors}},
  ]

  let layer_to_fit = communes_layer
  let layers = [communes_layer, flows_layer]

  return {layer_to_fit, layers, legend, sources}
}


function createClickableCommuneLayer(communes, clickFunction){
  let communes_g = [];
  for (var i=0; i<communes.length; i++){
    let geo_code = communes[i].geo_code
    for (let o of communes[i].outline){
      let commune = L.polygon(o, {
        color: "#fff",
        fillColor: c_light,
        weight: 1.5,
        opacity: 1,
        fillOpacity: 0.4,
      });
      managePopup(commune, "<p class='leaflet_map_popup'>" + communes[i].name + "</p>");

      commune.on('click', function (e) {
         clickFunction(geo_code)
      });
      communes_g.push(commune);
    }
  }
  let communes_layer = L.featureGroup(communes_g);
  return communes_layer
}
