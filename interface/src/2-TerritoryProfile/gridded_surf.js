import {GridLayer} from '../i-Map/Layers/GridLayer';

import {c_gradient_reds_greens} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';



function getGridLayer(objects, selected_filters){
  let {gridded_pop} = objects

  let grid_legend = {
    thresholds: [0, 20, 30, 40, 50, 60, 100],
    colors: c_gradient_reds_greens.slice(2, 8),
    title: `Surface moyenne par personne au carreau`,
    unit: "m²/pers",
    format: (d) => formatFigure(d)
  }

  let compute_value = (d) => d.population !== 0 ? Math.round(d.surface/d.population) : null

  let grid_layer = new GridLayer({
    grid: gridded_pop,
    getValue: (d) => compute_value(d),
    getLabel: (d) => compute_value(d) !== null ? `${formatFigure(compute_value(d))} m²/pers` : "indisponible",
    legend: grid_legend
  });

  return [grid_layer]
}


export const gridded_surf = new Indicator({
    indicator: "gridded_surf",
    label: "surface moyenne par personne au carreau",
    description: "La surface moyenne par personne au carreau (200m de côté) est le rapport entre la somme des surfaces des ménages du carreau et la population du carreau.",

    filters: [],

    tables: {},
    layers : {
      path: getGridLayer
    },

    datasets_names: ["territory/gridded_pop"]
  })
