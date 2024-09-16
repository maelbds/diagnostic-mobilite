import {CircleLayer} from '../i-Map/Layers/CircleLayer';
import {ChoroLayer} from '../i-Map/Layers/ChoroLayer';

import {c_gradient_reds_greens, c_yellow} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';



function getChoroLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects

  let value = (e) => e["workers"] === 0 ? null : Math.round(e["jobs"]/e["workers"]*100)
  let is_available = (e) => e["workers"] !== 0

  let choro_legend = {
    thresholds: [0, 35, 65, 100, 150, 200, 500],
    colors: c_gradient_reds_greens.slice(2, 8),
    references: [
      {label: "Territoire", value: formatFigure(value(mesh_elements_ref.territory))},
      {label: "Département", value: formatFigure(value(mesh_elements_ref.dep))},
      {label: "France", value: formatFigure(value(mesh_elements_ref.france))},
    ],
    title: `Indice de concentration de l'emploi`,
    unit: "",
    format: (d) => formatFigure(d)
  }

  let choro_layer = new ChoroLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => value(d),
    getLabel: (d) => is_available(d) ? `Indice de concentration de l'emploi : <b>${formatFigure(value(d))}</b> (${formatFigure(d.workers)} actifs, actives / ${formatFigure(d.jobs)} emplois)` : "<i>donnée indisponible</i>",
    legend: choro_legend
  });

  return [choro_layer]
}

function getCircleLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects

  let value = (d) => d.jobs
  let is_available = (e) => e["jobs"] !== null

  let circle_legend = {
    references: [
      {label: "Territoire", value: formatFigure(value(mesh_elements_ref.territory))},
    ],
    color: c_yellow,
    title: `Nombre d'emplois`,
    unit: "",
    format: (d) => formatFigure(parseFloat(parseFloat(d.toPrecision(2)).toFixed(0)))
  }

  let circle_layer = new CircleLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => value(d),
    getLabel: (d) => is_available(d) ? `<b>${formatFigure(value(d))}</b> emplois` : "<i>donnée indisponible</i>",
    legend: circle_legend
  });

  return [circle_layer]
}


function getMeshElementsTable(objects, selected_filters){
  let headlines = [], cols = [], format_table = [], format_csv = [], align = [];
  let mesh_elements = objects.mesh_elements_geojson.features.map((f) => f.properties)

  headlines.push("Nombre d'emplois")
  cols.push(mesh_elements.map((c)=> c[`jobs`]))
  format_table.push((f)=>formatFigure(f))
  format_csv.push((f)=>f)
  align.push("r")

  let value = (e) => e["workers"] === 0 ? null : Math.round(e["jobs"]/e["workers"]*100)

  headlines.push("Indice de concentration de l'emploi")
  cols.push(mesh_elements.map((c)=> value(c)))
  format_table.push((f)=>formatFigure(f))
  format_csv.push((f)=>f)
  align.push("r")

  return {headlines, cols, format_table, format_csv, align}
}


export const jobs = new Indicator({
    indicator: "jobs",
    label: "lieux d'emplois",
    data_source: "verified",

    tables: {
      mesh: getMeshElementsTable
    },
    layers : {
      circle: getCircleLayer,
      choropleth: getChoroLayer,
    },
    datasets_names: ["territory/jobs"]
})
