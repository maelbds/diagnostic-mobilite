import {CircleLayer} from '../i-Map/Layers/CircleLayer';
import {ChoroLayer} from '../i-Map/Layers/ChoroLayer';
import {PathLayer} from '../i-Map/Layers/PathLayer';

import {c_gradient_greens, c_yellow} from '../a-Graphic/Colors';
import {pattern_zfe} from '../a-Graphic/Layout';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';

import {CritairFilter} from '../h-Filters/CritairFilter'

var critair_legend = CritairFilter.legend


function getChoroLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects
  let {critair_filter} = selected_filters

  let sum = (e) => critair_filter.map(c=> e[c]).reduce((a,b)=>a+b, 0)
  let value = (e) => e["all"] === 0 ? 0 : Math.round(sum(e)/e["all"]*1000)/10

  let is_available = (e) => critair_filter.every((p) => `${p}` in e)

  let suffix_critair = critair_filter.map(c=>critair_legend[c]).join(", ")

  let choro_legend = {
    thresholds: objects.mesh_elements_leg[`t_${critair_filter.join("_")}`],
    colors: c_gradient_greens,
    references: [
      {label: "Territoire", value: formatFigure(value(mesh_elements_ref.territory))},
      {label: "Département", value: formatFigure(value(mesh_elements_ref.dep))},
      {label: "France", value: formatFigure(value(mesh_elements_ref.france))},
    ],
    title: `Part des véhicules ${suffix_critair}`,
    unit: "%",
    format: (d) => formatFigure(d)
  }

  let choro_layer = new ChoroLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => value(d),
    getLabel: (d) => is_available(d) ? `<b>${formatFigure(value(d))} %</b> de véhicules ${suffix_critair}` : "<i>donnée indisponible</i>",
    legend: choro_legend
  });

  return [choro_layer]
}

function getCircleLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects
  let {critair_filter} = selected_filters

  let sum = (e) => critair_filter.map(c=> e[c]).reduce((a,b)=>a+b, 0)
  let is_available = (e) => critair_filter.every((p) => `${p}` in e)

  let suffix_critair = critair_filter.map(c=>critair_legend[c]).join(", ")

  let circle_legend = {
    references: [
      {label: "Territoire", value: formatFigure(sum(mesh_elements_ref.territory))},
    ],
    color: c_yellow,
    title: `Nombre de véhicules ${suffix_critair}`,
    unit: "véh",
    format: (d) => formatFigure(parseFloat(parseFloat(d.toPrecision(2)).toFixed(0)))
  }

  let circle_layer = new CircleLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => sum(d),
    getLabel: (d) => is_available(d) ? `<b>${formatFigure(sum(d))}</b> véhicules ${suffix_critair}` : "<i>donnée indisponible</i>",
    legend: circle_legend
  });

  return [circle_layer]
}

function getZFELayer(objects, selected_filters){
  let {modes} = selected_filters
  let {zfe} = objects

  let zfe_legend = {
    pattern: pattern_zfe,
    title: `Périmètre ZFE`
  }

  let path_layer = new PathLayer({
    geojson: zfe,
    filter: (d) => true,
    getLabel: (d) => `<b>ZFE en vigueur à partir du ${(new Date(Date.parse(d.date_debut))).toLocaleDateString("fr-FR")}</b></br>Les véhicules particuliers avec une vignette ${d.vp_critair} et au-delà ne peuvent pas circuler (${d.vp_horaires})`,
    pattern: pattern_zfe,
    legend: zfe_legend,

  });

  return [path_layer]
}


function getMeshElementsTable(objects, selected_filters){
  let headlines = [], cols = [], format_table = [], format_csv = [], align = [];
  let mesh_elements = objects.mesh_elements_geojson.features.map((f) => f.properties)

  Object.keys(critair_legend).forEach((f_critair) => {
    headlines.push("Nombre de véhicules " + critair_legend[f_critair])
    cols.push(mesh_elements.map((c)=> c[`${f_critair}`]))
    format_table.push((f)=>formatFigure(f))
    format_csv.push((f)=>f)
    align.push("r")
  });

  return {headlines, cols, format_table, format_csv, align}
}


export const critair = new Indicator({
    indicator: "critair",
    label: "parc de voitures particulières",
    data_source: "verified",

    description: "Les vignettes Crit'Air reflètent l'ancienneté du parc de véhicules. Elles sont aussi à considérer dans le cas d'un territoire soumis à une ZFE (zone à faible émission).",

    filters: [CritairFilter],

    tables: {
      mesh: getMeshElementsTable
    },
    layers : {
      circle: getCircleLayer,
      choropleth: getChoroLayer,
      path: getZFELayer
    },
    datasets_names: ["offer/critair", "offer/zfe"]
})
