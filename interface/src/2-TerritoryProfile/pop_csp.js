import {CircleLayer} from '../i-Map/Layers/CircleLayer';
import {ChoroLayer} from '../i-Map/Layers/ChoroLayer';

import {c_gradient_greens, c_yellow} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';

import {GenderFilter} from '../h-Filters/GenderFilter'
import {CSPFilter} from '../h-Filters/CSPFilter'

var csp_filter = CSPFilter.labels
var gender_filter = GenderFilter.labels


function getChoroLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects
  let {gender, pop_csp} = selected_filters

  let sum_csp = (e) => pop_csp.map(c=> e[gender+"15P_CS"+c]).reduce((a,b)=>a+b, 0)
  let value = (e) => e[gender+"15P"] === 0 ? 0 : Math.round(sum_csp(e)/e[gender+"15P"]*1000)/10

  let is_available = (e) => pop_csp.every((p) => `${gender}15P_CS${p}` in e)

  let suffix_csp = pop_csp.map(c=>csp_filter[c].toLowerCase()).join(", ")
  let suffix_gender = gender_filter[gender]

  let choro_legend = {
    thresholds: objects.mesh_elements_leg[`${gender}15P_CS_${pop_csp.join("_")}`],
    colors: c_gradient_greens,
    references: [
      {label: "Territoire", value: formatFigure(value(mesh_elements_ref.territory))},
      {label: "Département", value: formatFigure(value(mesh_elements_ref.dep))},
      {label: "France", value: formatFigure(value(mesh_elements_ref.france))},
    ],
    title: `Part des ${suffix_csp} parmi la population -  ${suffix_gender}`,
    unit: "%",
    format: (d) => formatFigure(d)
  }

  let choro_layer = new ChoroLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => value(d),
    getLabel: (d) => is_available(d) ? `<b>${formatFigure(value(d))} %</b> de ${suffix_csp} parmi la population des plus de 15 ans -  ${suffix_gender}` : "<i>donnée indisponible</i>",
    legend: choro_legend
  });

  return [choro_layer]
}

function getCircleLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects
  let {gender, pop_csp} = selected_filters

  let sum_csp = (e) => pop_csp.map(c=> e[gender+"15P_CS"+c]).reduce((a,b)=>a+b, 0)
  let is_available = (e) => pop_csp.every((p) => `${gender}15P_CS${p}` in e)

  let suffix_csp = pop_csp.map(c=>csp_filter[c].toLowerCase()).join(", ")
  let suffix_gender = gender_filter[gender]

  let circle_legend = {
    references: [
      {label: "Territoire", value: formatFigure(sum_csp(mesh_elements_ref.territory))},
    ],
    color: c_yellow,
    title: `Population des ${suffix_csp} -  ${suffix_gender}`,
    unit: "hab",
    format: (d) => formatFigure(parseFloat(parseFloat(d.toPrecision(2)).toFixed(0)))
  }

  let circle_layer = new CircleLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => sum_csp(d),
    getLabel: (d) => is_available(d) ? `<b>${formatFigure(sum_csp(d))}</b> ${suffix_csp} -  ${suffix_gender}` : "<i>donnée indisponible</i>",
    legend: circle_legend
  });

  return [circle_layer]
}


function getMeshElementsTable(objects, selected_filters){
  let headlines = [], cols = [], format_table = [], format_csv = [], align = [];
  let mesh_elements = objects.mesh_elements_geojson.features.map((f) => f.properties)

  Object.keys(csp_filter).forEach((f_csp) => {
    Object.keys(gender_filter).forEach((f_gender) => {
      headlines.push("Population des " + csp_filter[f_csp] + " - " + gender_filter[f_gender])
      cols.push(mesh_elements.map((c)=> c[`${f_gender}15P_CS${f_csp}`]))
      format_table.push((f)=>formatFigure(f))
      format_csv.push((f)=>f)
      align.push("r")
    });
  });

  return {headlines, cols, format_table, format_csv, align}
}


export const pop_csp = new Indicator({
    indicator: "pop_csp",
    label: "population par catégories socio-professionnelles",
    data_source: "verified",

    filters: [GenderFilter, CSPFilter],

    tables: {
      mesh: getMeshElementsTable
    },
    layers : {
      circle: getCircleLayer,
      choropleth: getChoroLayer
    },
    datasets_names: ["territory/pop_csp"]
})
