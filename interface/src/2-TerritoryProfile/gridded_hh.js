import {GridLayer} from '../i-Map/Layers/GridLayer';

import {c_gradient_reds_greens} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';



function getGridLayer(objects, selected_filters){
  let {gridded_pop} = objects

  let grid_legend = {
    thresholds: [1, 2, 2.2, 2.4, 2.6, 2.8, 10],
    colors: c_gradient_reds_greens.slice(3, 9),
    title: `Taille moyenne des ménages au carreau`,
    unit: "hab/ménage",
    format: (d) => formatFigure(d)
  }

  let compute_value = (d) => d.households !== 0 ? Math.round(d.population/d.households*10)/10 : null

  let grid_layer = new GridLayer({
    grid: gridded_pop,
    getValue: (d) => compute_value(d),
    getLabel: (d) => compute_value(d) !== null ? `${formatFigure(compute_value(d))} hab/ménage` : "indisponible",
    legend: grid_legend
  });

  return [grid_layer]
}


export const gridded_hh = new Indicator({
    indicator: "gridded_hh",
    label: "taille moyenne des ménages au carreau",
    description: "La taille moyenne des ménages au carreau (200m de côté) est le rapport entre la population du carreau et le nombre de ménages du carreau.",

    filters: [],

    tables: {},
    layers : {
      path: getGridLayer
    },

    datasets_names: ["territory/gridded_pop"]
  })
