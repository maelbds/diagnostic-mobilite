import {PointLayer} from '../i-Map/Layers/PointLayer';
import {GridLayer} from '../i-Map/Layers/GridLayer';

import {c_gradient_greens} from '../a-Graphic/Colors';
import {pattern_grocery_conv, pattern_grocery_super, pattern_grocery_hyper} from '../a-Graphic/Layout';

import {cols_to_rows, formatFigure} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';


const legend = {
  "convenience store": {
    title: "Épicerie",
    pattern: pattern_grocery_conv
  },
  "supermarket": {
    title: "Supermarché",
    pattern: pattern_grocery_super
  },
  "hypermarket": {
    title: "Hypermarché",
    pattern: pattern_grocery_hyper
  },
}


function getGroceryLayer(objects, selected_filters, type){
  let {modes} = selected_filters
  let {grocery} = objects

  let pt_legend = {
    pattern: legend[type].pattern,
    title: legend[type].title,
    subtitle: legend[type].subtitle
  }

  let cluster_layer = new PointLayer({
    geojson: grocery,
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
    layers = layers.concat(getGroceryLayer(objects, selected_filters, type))
  });
  return layers
}



export const places_grocery = new Indicator({
    indicator: "places_grocery",
    label: "commerces alimentaires",

    filters: [],

    tables: {},
    layers : {
      path: getAllLayer,
    },

    datasets_names: ["territory/grocery", "territory/gridded_pop"]
  })
