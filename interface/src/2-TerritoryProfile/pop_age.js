import {CircleLayer} from '../i-Map/Layers/CircleLayer';
import {ChoroLayer} from '../i-Map/Layers/ChoroLayer';

import {c_gradient_greens, c_yellow} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';

import {GenderFilter} from '../h-Filters/GenderFilter'
import {PopAgeFilter} from '../h-Filters/PopAgeFilter'

var age_filter = PopAgeFilter.labels
var gender_filter = GenderFilter.labels


function getChoroLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects
  let {gender, pop_age} = selected_filters

  let sum_age = (e) => pop_age.map(c=> e[gender+""+c]).reduce((a,b)=>a+b, 0)
  let value = (e) => e[gender+"_all"] === 0 ? 0 : Math.round(sum_age(e)/e[gender+"_all"]*1000)/10

  let is_available = (e) => pop_age.every((p) => `${gender}${p}` in e)

  let suffix_age = pop_age.map(c=>age_filter[c].toLowerCase()).join(", ")
  let suffix_gender = gender_filter[gender]

  let choro_legend = {
    thresholds: objects.mesh_elements_leg[`r_all_${pop_age.join("_")}`],
    colors: c_gradient_greens,
    references: [
      {label: "Territoire", value: formatFigure(value(mesh_elements_ref.territory))},
      {label: "Département", value: formatFigure(value(mesh_elements_ref.dep))},
      {label: "France", value: formatFigure(value(mesh_elements_ref.france))},
    ],
    title: `Part des ${suffix_age} parmi la population -  ${suffix_gender}`,
    unit: "%",
    format: (d) => formatFigure(d)
  }

  let choro_layer = new ChoroLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => value(d),
    getLabel: (d) => is_available(d) ? `<b>${formatFigure(value(d))} %</b> de ${suffix_age} parmi la population -  ${suffix_gender}` : "<i>donnée indisponible</i>",
    legend: choro_legend
  });

  return [choro_layer]
}

function getCircleLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects
  let {gender, pop_age} = selected_filters

  let sum_age = (e) => pop_age.map(c=> e[`${gender}${c}`]).reduce((a,b)=>a+b, 0)
  let is_available = (e) => pop_age.every((p) => `${gender}${p}` in e)

  let suffix_age = pop_age.map(c=>age_filter[c].toLowerCase()).join(", ")
  let suffix_gender = gender_filter[gender]

  let circle_legend = {
    references: [
      {label: "Territoire", value: formatFigure(sum_age(mesh_elements_ref.territory))},
    ],
    color: c_yellow,
    title: `Population des ${suffix_age} -  ${suffix_gender}`,
    unit: "hab",
    format: (d) => formatFigure(parseFloat(parseFloat(d.toPrecision(2)).toFixed(0)))
  }

  let circle_layer = new CircleLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => sum_age(d),
    getLabel: (d) => is_available(d) ? `<b>${formatFigure(sum_age(d))} hab</b> de ${suffix_age} -  ${suffix_gender}` : "<i>donnée indisponible</i>",
    legend: circle_legend
  });

  return [circle_layer]
}


function getMeshElementsTable(objects, selected_filters){
  let headlines = [], cols = [], format_table = [], format_csv = [], align = [];
  let mesh_elements = objects.mesh_elements_geojson.features.map((f) => f.properties)

  Object.keys(age_filter).forEach((f_age) => {
    Object.keys(gender_filter).forEach((f_gender) => {
      headlines.push("Population des " + age_filter[f_age] + " - " + gender_filter[f_gender])
      cols.push(mesh_elements.map((c)=> c[f_gender+f_age]))
      format_table.push((f)=>formatFigure(f))
      format_csv.push((f)=>f)
      align.push("r")
    });
  });

  return {headlines, cols, format_table, format_csv, align}
}


export const pop_age = new Indicator({
    indicator: "pop_age",
    label: "population par tranches d'âge",
    data_source: "verified",

    filters: [GenderFilter, PopAgeFilter],

    tables: {
      mesh: getMeshElementsTable
    },
    layers : {
      circle: getCircleLayer,
      choropleth: getChoroLayer
    },
    datasets_names: ["territory/population"]
})
