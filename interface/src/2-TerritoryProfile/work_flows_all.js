import React, { Component } from 'react';
import {c_gradient_reds} from '../a-Graphic/Colors';
import {formatFigure, titleCase} from '../f-Utilities/util_func'

import {getLegendMode} from '../b-LeafletMap/leaflet_map';
import {createFlowsLayer} from '../b-LeafletMap/LeafletMapElement/createFlow'
import {createCommuneBordersLayer} from '../b-LeafletMap/LeafletMapElement/createCommune'

const L = window.L;


var f_limit = 20;


export function getWorkFlowsAllElements(communes, influence_communes, work_communes, limit_flows_nb, selectCommuneAllLimit){

  // dictionnaries geocode to name & geocode to coords for all communes
  let communes_geo_codes_to_coords = {};
  communes.concat(influence_communes).concat(work_communes).map((c) => communes_geo_codes_to_coords[c.geo_code] = c.center)
  let communes_geo_codes_to_names = {};
  communes.concat(influence_communes).concat(work_communes).map((c) => communes_geo_codes_to_names[c.geo_code] = c.name)

  // all flows
  let flows = []
  communes.forEach((c, i) => {
    Object.keys(c.flows_home_work).filter((c_geo)=> c.flows_home_work[c_geo]>f_limit).forEach((c_geo) => {
      flows.push({
        coords: [c.center, communes_geo_codes_to_coords[c_geo]],
        mass: c.flows_home_work[c_geo],
        label: c.name + " → " + communes_geo_codes_to_names[c_geo]  + " : " + formatFigure(c.flows_home_work[c_geo]) + " navetteurs"
      })
    })

    let within_flow = parseInt(c.workers_within_commune_prop * c.status.employed)
    if (within_flow >= 30){
      flows.push({
        coords: [c.center, c.center],
        mass: within_flow,
        label: c.name + " → " + c.name  + " : " + formatFigure(within_flow) + " navetteurs"
      })
    }
  });

  flows = flows.sort(((a,b)=> b.mass - a.mass))
  flows = flows.slice(0, limit_flows_nb)

  let flows_coords = flows.map((f) => f.coords)
  let flows_masses = flows.map((f) => f.mass)
  let flows_labels = flows.map((f) => f.label)


  let mode = "ckmeans"
  let legend_label = "Flux principaux "
  let legend_unit = "(nombre de navetteurs)"
  let colors = c_gradient_reds
  let sources = ["mobpro"]

  let legend_values = flows_masses

  // --- create layers
  let communes_layer = createCommuneBordersLayer(communes)
  let flows_layer = createFlowsLayer(flows_coords, flows_masses, flows_labels, mode, colors);

  let [legend_intervals, legend_colors] = getLegendMode(mode, legend_values, colors)
  let legend = [
    {type: "LegendDescription", params: {desc: "Vue d'ensemble des navetteurs habitant le territoire."}},
    {type: "LegendCursor", params: {min: 25,
                                    max: 200,
                                    step: 25,
                                    id: "flows_all",
                                    value: limit_flows_nb,
                                    cursorFunction: selectCommuneAllLimit}},
    {type: "LegendDescription", params: {desc: "Seuls les " + limit_flows_nb + " flux les plus importants sont affichés (de plus de 20 navetteurs)."}},
    {type: "LegendSpace", params: {}},
    {type: "LegendLabel", params: {label: legend_label, unit: legend_unit}},
    {type: "LegendValuesFlows", params: {intervals: legend_intervals, colors: legend_colors}},
  ]

  let layer_to_fit = communes_layer
  let layers = [communes_layer, flows_layer]

  return {layer_to_fit, layers, legend, sources}
}


export function getFlowsTable(communes, influence_communes, work_communes){

  // dictionnaries geocode to name & geocode to coords for all communes
  let communes_geo_codes_to_coords = {};
  communes.concat(influence_communes).concat(work_communes).map((c) => communes_geo_codes_to_coords[c.geo_code] = c.center)
  let communes_geo_codes_to_names = {};
  communes.concat(influence_communes).concat(work_communes).map((c) => communes_geo_codes_to_names[c.geo_code] = c.name)

  // all internal flows
  let flows = []
  communes.forEach((c, i) => {
    Object.keys(c.flows_home_work).filter((c_geo)=> c.flows_home_work[c_geo]>f_limit).forEach((c_geo) => {
      flows.push({
        geo_code_ori: c.geo_code,
        name_ori: c.name,
        geo_code_des: c_geo,
        name_des: communes_geo_codes_to_names[c_geo],
        flow: c.flows_home_work[c_geo],
      })
    })

    let within_flow = parseInt(c.workers_within_commune_prop * c.status.employed)
    if (within_flow >= 30){
      flows.push({
        geo_code_ori: c.geo_code,
        name_ori: c.name,
        geo_code_des: c.geo_code,
        name_des: c.name,
        flow: within_flow,
      })
    }
  });

  flows = flows.sort(((a,b)=> b.flow - a.flow))

  // all flows from outside
  let flows_ext = []
  communes.forEach((c, i) => {
    Object.keys(c.flows_home_work_workers).filter((c_geo)=> c.flows_home_work_workers[c_geo]["flow"]>f_limit)
                                          .filter((c_geo)=> !communes.map((c)=>c.geo_code).includes(c_geo)).forEach((c_geo) => {
      flows_ext.push({
        geo_code_ori: c_geo,
        name_ori: titleCase(c.flows_home_work_workers[c_geo]["name"]),
        geo_code_des: c.geo_code,
        name_des: c.name,
        flow: c.flows_home_work_workers[c_geo]["flow"],
      })
    })
  });

  flows_ext = flows_ext.sort(((a,b)=> b.flow - a.flow))


  let headlines=["Code Insee Origine", "Commune Origine", "Code Insee Destination", "Commune Destination", "Nombre de navettes domicile→travail (flux)"]
  let rows_int= flows.map((f)=> Object.values(f))
  let row_title= [["Flux depuis l'extérieur", null, null, null, null]]
  let rows_ext= flows_ext.map((f)=> Object.values(f))
  let rows = rows_int.concat(row_title, rows_ext)
  let format_table=[(f)=>f, (f)=>f, (f)=>f, (f)=>f, (f)=>formatFigure(f)]
  let format_csv=[(f)=>f, (f)=>f, (f)=>f, (f)=>f, (f)=>f]
  let align=["l", "l", "l", "l", "r"]

  let sources_table = ["mobpro"]
  let name_csv= "flux_domicile_travail"
  return {headlines, rows, align, format_table, format_csv, sources_table, name_csv}
}



/* OLD CODE

// compute prop external/internal work distance
let internal_flows_distance = communes.map((c) => Object.keys(c.flows_home_work)
                                        .filter((c_geo)=> communes.map((co)=>co.geo_code).includes(c_geo) && c.flows_home_work[c_geo]>f_limit_all)
                                        .map((c_geo) => c.flows_home_work[c_geo] * calcDist(c.center, communes_geo_codes_to_coords[c_geo]))
                                        .reduce((a, b) => a + b, 0)).reduce((a, b) => a + b, 0)
let total_flows_distance = communes.map((c) => Object.keys(c.flows_home_work)
                                        .filter((c_geo)=> c.flows_home_work[c_geo]>f_limit_all)
                                        .map((c_geo) => c.flows_home_work[c_geo] * calcDist(c.center, communes_geo_codes_to_coords[c_geo]))
                                        .reduce((a, b) => a + b, 0)).reduce((a, b) => a + b, 0)
this.prop_external_work_distance = Math.round(100 - internal_flows_distance/total_flows_distance*100)
*/
