import {CircleLayer} from '../i-Map/Layers/CircleLayer';

import {c_gradient_greens, c_yellow} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';

import {GenderFilter} from '../h-Filters/GenderFilter'

var gender_filter = GenderFilter.labels
var gender_filter_legend = GenderFilter.legend


function getCircleLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects
  let {gender} = selected_filters

  let key = "pop_" + gender

  let circle_legend = {
    references: [{label: "Territoire", value: formatFigure(mesh_elements_ref.territory[key])}],
    color: c_yellow,
    title: `Population - ${gender_filter[gender]}`,
    unit: "hab",
    format: (d) => formatFigure(parseFloat(parseFloat(d.toPrecision(2)).toFixed(0)))
  }

  let circle_layer = new CircleLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => d[key],
    getLabel: (d) => key in d ? `${formatFigure(d[key])} ${gender_filter_legend[gender]}` : "<i>donnée indisponible</i>",
    legend: circle_legend
  });

  return [circle_layer]
}


function getMeshElementsTable(objects, selected_filters){
  let headlines = [], cols = [], format_table = [], format_csv = [], align = [];
  let mesh_elements = objects.mesh_elements_geojson.features.map((f) => f.properties)

  Object.keys(gender_filter).forEach((f_gender) => {
    headlines.push("Population - " + gender_filter[f_gender])
    cols.push(mesh_elements.map((c)=> c["pop_" + f_gender]))
    format_table.push((f)=>formatFigure(f))
    format_csv.push((f)=>f)
    align.push("r")
  });

  return {headlines, cols, format_table, format_csv, align}
}


export const population = new Indicator({
    indicator: "population",
    label: "population",

    filters: [GenderFilter],

    tables: {
      mesh: getMeshElementsTable
    },
    layers : {
      circle: getCircleLayer
    },

    datasets_names: ["territory/population"]
  })
