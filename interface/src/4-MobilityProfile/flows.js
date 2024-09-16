import {FlowLayer} from '../i-Map/Layers/FlowLayer';

import {c_gradient_reds, c_yellow} from '../a-Graphic/Colors';
import {pattern_flows} from '../a-Graphic/Layout';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import * as ss from "simple-statistics";

import {Indicator} from '../g-Components/Indicator';

import {FlowLimitFilter} from '../h-Filters/FlowLimitFilter';
import {NbDistFilter} from '../h-Filters/NbDistFilter';

var nb_dist_legend = NbDistFilter.legend


function getPathLayer(objects, selected_filters){
  let {flows, mesh_elements_ref, mesh_elements_leg} = objects
  let {flow_limit_filter, nb_dist_filter} = selected_filters

  let value = (e) => e[nb_dist_filter]
  let getValue = (d) => value(d.properties)
  let total = flows.features.map(getValue).reduce((a, b) => a+b, 0)
  let valueProp = (d) => d.properties["prop_" + nb_dist_filter] //Math.round(value(d.properties)/total * 1000)/10

  let limit = flow_limit_filter === "all" ? 10000 : parseInt(flow_limit_filter)
  let sort = (a, b) => value(b.properties) - value(a.properties)
  let filter = (d) => d //.properties.sample > 25 DONE IN BACKEND

  let all_values = flows.features.filter(filter).sort(sort).slice(0, limit).map(getValue)

  let clusters, thresholds, colors;
  if (all_values.length === 0){
    thresholds = [0, 25, 50, 100, 200, 500, 1000, 2000, 5000].slice(0, pattern_flows.colors.length + 1)
    colors = pattern_flows.colors
  }
  else if (all_values.length < pattern_flows.colors.length){
    clusters = all_values.sort().map((c) => [c, c])

    thresholds = clusters.slice(0, -1).map((c, i) => (c[1] + clusters[i+1][1]) / 2)
    thresholds.unshift(clusters[0][0])
    thresholds.push(clusters[clusters.length-1][1])

    colors = pattern_flows.colors.slice(0, all_values.length)
  }
  else {
    clusters = ss.ckmeans(all_values, pattern_flows.colors.length)
    clusters = clusters.map((c) => [c[0], c[c.length-1]])

    thresholds = clusters.slice(0, -1).map((c, i) => (c[1] + clusters[i+1][1]) / 2)
    thresholds.unshift(clusters[0][0])
    thresholds.push(clusters[clusters.length-1][1])

    colors = pattern_flows.colors
  }

  let path_legend = {
    thresholds: thresholds,
    colors: colors,
    strokes: pattern_flows.strokes,
    radius: pattern_flows.radius,
    references: [],
    title: `Flux`,
    subtitle: `(${nb_dist_legend[nb_dist_filter]}/jour)`,
    unit: "",
    format: (d) => formatFigure(parseFloat(parseFloat(d.toPrecision(2)).toFixed(0)))
  }

  let path_layer = new FlowLayer({
    geojson: flows,
    getValue: getValue,
    getLabel: (d) => `${d.properties.ori_name} ↔ ${d.properties.des_name} : <b>${formatFigure(value(d.properties))}</b> ${nb_dist_legend[nb_dist_filter]}/jour (soit ${formatFigure(valueProp(d))}% de l'ensemble)`,
    filter: filter,
    sort: sort,
    limit: limit,
    legend: path_legend,
    bidirectionnal: true,
  });

  return [path_layer]
}


function getElementsTable(objects, selected_filters){
  let headlines = [], cols = [], format_table = [], format_csv = [], align = [];
  let {flows} = objects

  let sort = (a, b) => b.properties.number - a.properties.number
  let filter = (d) => d //.properties.sample > 25 DONE IN BACKEND

  let flows_table = flows.features.filter(filter).sort(sort)

  headlines = ["Code A", "Nom A", "Code B", "Nom B", "Flux A↔B (déplacements)", "Flux A↔B (distance en km)"]
  cols = [flows_table.map((c)=> c.properties.ori_geo_code),
           flows_table.map((c)=> c.properties.ori_name),
           flows_table.map((c)=> c.properties.des_geo_code),
           flows_table.map((c)=> c.properties.des_name),
           flows_table.map((c)=> c.properties.number),
           flows_table.map((c)=> c.properties.distance), ]
  format_table = [(f)=>f, (f)=>f, (f)=>f, (f)=>f, (f)=>formatFigure(f), (f)=>formatFigure(f)]
  format_csv = [(f)=>f, (f)=>f, (f)=>f, (f)=>f, (f)=>f, (f)=>f]
  align = ["l", "l", "l", "l", "r", "r"]

  return {headlines, cols, format_table, format_csv, align}
}


export const flows = new Indicator({
    indicator: "flows",
    label: "tous les flux",
    data_source: "computed",
    data_source_from_request: true,
    data_source_function: (objects) => objects.sources.map((s) => s.label).includes("Enquête Mobilité des personnes (SDES 2019)") ? "model" : "emd",
    description: "On représente ici les flux tous modes et tous motifs confondus. Seuls les flux avec une pertinence statistique suffisante sont affichés.",

    filters: [NbDistFilter, FlowLimitFilter],

    tables: {
      elements: getElementsTable
    },
    layers : {
      path: getPathLayer,
    },
    datasets_names: ["mobility/flows"]
})
