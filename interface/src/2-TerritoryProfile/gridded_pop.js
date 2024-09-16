import {GridLayer} from '../i-Map/Layers/GridLayer';

import {c_gradient_greens} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';



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


export const gridded_pop = new Indicator({
    indicator: "gridded_pop",
    label: "population carroyée",
    description: "La population carroyée est la population par carreau de 200m de côté.",

    filters: [],

    tables: {},
    layers : {
      path: getGridLayer
    },

    datasets_names: ["territory/gridded_pop"]
  })
