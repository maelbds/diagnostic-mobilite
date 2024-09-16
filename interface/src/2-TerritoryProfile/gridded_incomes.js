import {GridLayer} from '../i-Map/Layers/GridLayer';

import {c_gradient_reds_greens} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';



function getGridLayer(objects, selected_filters){
  let {gridded_pop} = objects

  let grid_legend = {
    thresholds: [600, 1600, 1750, 1930, 2050, 2200, 7000],
    colors: c_gradient_reds_greens.slice(2, 8),
    title: `Niveau de vie moyen`,
    unit: "€/uc/mois",
    format: (d) => formatFigure(d)
  }

  let compute_value = (d) => d.population !== 0 ? Math.round(d.incomes/d.population/12) : null

  let grid_layer = new GridLayer({
    grid: gridded_pop,
    getValue: (d) => compute_value(d),
    getLabel: (d) => compute_value(d) !== null ? `${formatFigure(compute_value(d))} €/uc/mois` : "indisponible",
    legend: grid_legend
  });

  return [grid_layer]
}


export const gridded_incomes = new Indicator({
    indicator: "gridded_incomes",
    label: "niveau de vie moyen au carreau",
    description: "Le niveau de vie moyen au carreau (200m de côté) correspond à la somme des niveaux de vie winsorisés des individus du carreau divisé par le nombre d'individus du carreau. On parle toujours du revenu disponible.",

    filters: [],

    tables: {},
    layers : {
      path: getGridLayer
    },

    datasets_names: ["territory/gridded_pop"]
  })
