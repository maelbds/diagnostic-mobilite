import {FlowLayer} from '../i-Map/Layers/FlowLayer';

import {c_gradient_reds, c_yellow} from '../a-Graphic/Colors';
import {pattern_flows} from '../a-Graphic/Layout';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import * as ss from "simple-statistics";

import {Indicator} from '../g-Components/Indicator';

import {FlowLimitFilter} from '../h-Filters/FlowLimitFilter';


function getPathLayer(objects, selected_filters){
  let {work_flows, mesh_elements_ref, mesh_elements_leg} = objects
  let {flow_limit_filter} = selected_filters

  let value = (e) => e.flow
  let getValue = (d) => value(d.properties)

  let limit = flow_limit_filter === "all" ? 10000 : parseInt(flow_limit_filter)
  let sort = (a, b) => value(b.properties) - value(a.properties)
  let filter = (d) => d.properties.flow > 25 && d.properties.distance < 100

  let all_values = work_flows.features.filter(filter).sort(sort).slice(0, limit).map(getValue)

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
    title: `Flux domicile → travail`,
    subtitle: "(nombre de navetteurs et navetteuses)",
    unit: "",
    format: (d) => formatFigure(parseFloat(parseFloat(d.toPrecision(2)).toFixed(0)))
  }

  let path_layer = new FlowLayer({
    geojson: work_flows,
    getValue: getValue,
    getLabel: (d) => `${d.properties.home_name} → ${d.properties.work_name} : <b>${formatFigure(value(d.properties))}</b> navetteurs et navetteuses`,
    filter: filter,
    sort: sort,
    limit: limit,
    legend: path_legend
  });

  return [path_layer]
}


function getElementsTable(objects, selected_filters){
  let headlines = [], cols = [], format_table = [], format_csv = [], align = [];
  let {work_flows} = objects

  let sort = (a, b) => b.properties.flow - a.properties.flow
  let filter = (d) => d.properties.flow > 25 && d.properties.distance < 100

  let flows = work_flows.features.filter(filter).sort(sort)

  headlines = ["Code origine", "Nom origine", "Code destination", "Nom destination", "Flux navetteurs et navetteuses"]
  cols = [flows.map((c)=> c.properties.home_geo_code),
               flows.map((c)=> c.properties.home_name),
               flows.map((c)=> c.properties.work_geo_code),
               flows.map((c)=> c.properties.work_name),
               flows.map((c)=> c.properties.flow), ]
  format_table = [(f)=>f, (f)=>f, (f)=>f, (f)=>f, (f)=>formatFigure(f)]
  format_csv = [(f)=>f, (f)=>f, (f)=>f, (f)=>f, (f)=>f]
  align = ["l", "l", "l", "l", "r"]

  return {headlines, cols, format_table, format_csv, align}
}


export const work_flows = new Indicator({
    indicator: "work_flows",
    label: "flux domicile → travail",
    data_source: "verified",
    description: "Les flux représentés concernent les actifs de 15 ans ou plus ayant un emploi et habitant le territoire d'étude. Ils relient leur commune de résidence et la commune dans laquelle ils déclarent travailler. Il mesure donc un nombre de « migrants alternants » ou « navettes » et non un nombre de déplacements effectifs. La fréquence (quotidienne, hebdomadaire, etc.) des déplacements n’est pas observée.",

    filters: [FlowLimitFilter],

    tables: {
      elements: getElementsTable
    },
    layers : {
      path: getPathLayer,
    },
    datasets_names: ["territory/work_flows"]
})
