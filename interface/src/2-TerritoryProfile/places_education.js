import {PointLayer} from '../i-Map/Layers/PointLayer';
import {GridLayer} from '../i-Map/Layers/GridLayer';

import {c_gradient_greens} from '../a-Graphic/Colors';
import {pattern_school_0, pattern_school_1, pattern_school_2, pattern_school_3, pattern_school_4} from '../a-Graphic/Layout';

import {cols_to_rows, formatFigure} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';


const legend = {
  "pre school": {
    title: "École maternelle",
    pattern: pattern_school_0
  },
  "primary school": {
    title: "École primaire",
    pattern: pattern_school_1
  },
  "secondary school": {
    title: "Collège",
    pattern: pattern_school_2
  },
  "high school": {
    title: "Lycée",
    pattern: pattern_school_3
  },
  "university": {
    title: "Université",
    pattern: pattern_school_4
  }
}


function getEducationLayer(objects, selected_filters, type){
  let {modes} = selected_filters
  let {education} = objects

  let pt_legend = {
    pattern: legend[type].pattern,
    title: legend[type].title,
    subtitle: legend[type].subtitle
  }

  let cluster_layer = new PointLayer({
    geojson: education,
    filter: (d) => d.properties.type === type,
    getLabel: (d) => d.name,
    pattern: legend[type].pattern,
    legend: pt_legend,

  });

  return [cluster_layer]
}

function getGridLayer(objects, selected_filters){
  let {gridded_pop} = objects

  let grid_legend = {
    thresholds: [1, 25, 100, 250, 500, 2000],
    colors: c_gradient_greens,
    title: `Population au carreau (200m)`,
    unit: "hab",
    format: (d) => formatFigure(d)
  }

  let grid_layer = new GridLayer({
    grid: gridded_pop,
    getValue: (d) => d.population,
    getLabel: (d) => `${formatFigure(d.population)} hab`,
    legend: grid_legend
  });

  return [grid_layer]
}

function getAllLayer(objects, selected_filters){
  let layers = []
  layers = layers.concat(getGridLayer(objects, selected_filters))
  Object.keys(legend).reverse().forEach((type) => {
    layers = layers.concat(getEducationLayer(objects, selected_filters, type))
  });
  return layers
}



export const places_education = new Indicator({
    indicator: "places_education",
    label: "éducation",

    filters: [],

    tables: {},
    layers : {
      path: getAllLayer,
    },

    datasets_names: ["territory/education", "territory/gridded_pop"]
  })
