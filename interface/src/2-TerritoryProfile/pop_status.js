import {CircleLayer} from '../i-Map/Layers/CircleLayer';
import {ChoroLayer} from '../i-Map/Layers/ChoroLayer';

import {c_gradient_greens, c_yellow} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';

import {StatusFilter} from '../h-Filters/StatusFilter'

var status_filter = StatusFilter.labels


function getChoroLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects
  let {pop_status} = selected_filters

  let sum = (e) => pop_status.map(c=> e[c]).reduce((a,b)=>a+b, 0)
  let value = (e) => e["all"] === 0 ? 0 : Math.round(sum(e)/e["all"]*1000)/10

  let is_available = (e) => pop_status.every((p) => `${p}` in e)

  let suffix_status = pop_status.map(c=>status_filter[c].toLowerCase()).join(", ")

  let choro_legend = {
    thresholds: objects.mesh_elements_leg[`t_${pop_status.join("_")}`],
    colors: c_gradient_greens,
    references: [
      {label: "Territoire", value: formatFigure(value(mesh_elements_ref.territory))},
      {label: "Département", value: formatFigure(value(mesh_elements_ref.dep))},
      {label: "France", value: formatFigure(value(mesh_elements_ref.france))},
    ],
    title: `Part des personnes ${suffix_status} parmi la population`,
    unit: "%",
    format: (d) => formatFigure(d)
  }

  let choro_layer = new ChoroLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => value(d),
    getLabel: (d) => is_available(d) ? `<b>${formatFigure(value(d))} %</b> de personnes ${suffix_status} parmi la population` : "<i>donnée indisponible</i>",
    legend: choro_legend
  });

  return [choro_layer]
}

function getCircleLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects
  let {pop_status} = selected_filters

  let sum = (e) => pop_status.map(c=> e[c]).reduce((a,b)=>a+b, 0)
  let is_available = (e) => pop_status.every((p) => `${p}` in e)

  let suffix_status = pop_status.map(c=>status_filter[c].toLowerCase()).join(", ")

  let circle_legend = {
    references: [
      {label: "Territoire", value: formatFigure(sum(mesh_elements_ref.territory))},
    ],
    color: c_yellow,
    title: `Nombre de personnes ${suffix_status}`,
    unit: "hab",
    format: (d) => formatFigure(parseFloat(parseFloat(d.toPrecision(2)).toFixed(0)))
  }

  let circle_layer = new CircleLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => sum(d),
    getLabel: (d) => is_available(d) ? `<b>${formatFigure(sum(d))}</b> ${suffix_status}` : "<i>donnée indisponible</i>",
    legend: circle_legend
  });

  return [circle_layer]
}


function getMeshElementsTable(objects, selected_filters){
  let headlines = [], cols = [], format_table = [], format_csv = [], align = [];
  let mesh_elements = objects.mesh_elements_geojson.features.map((f) => f.properties)

  Object.keys(status_filter).forEach((f_status) => {
    headlines.push("Nombre de personnes " + status_filter[f_status])
    cols.push(mesh_elements.map((c)=> c[`${f_status}`]))
    format_table.push((f)=>formatFigure(f))
    format_csv.push((f)=>f)
    align.push("r")
  });

  return {headlines, cols, format_table, format_csv, align}
}


export const pop_status = new Indicator({
    indicator: "pop_status",
    label: "population par statut",
    data_source: "verified",

    filters: [StatusFilter],

    tables: {
      mesh: getMeshElementsTable
    },
    layers : {
      circle: getCircleLayer,
      choropleth: getChoroLayer
    },
    datasets_names: ["territory/pop_status"]
})
