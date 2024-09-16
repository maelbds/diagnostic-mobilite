import {PointLayer} from '../i-Map/Layers/PointLayer';
import {GridLayer} from '../i-Map/Layers/GridLayer';

import {c_gradient_greens} from '../a-Graphic/Colors';
import {pattern_cluster_0, pattern_cluster_1, pattern_cluster_2} from '../a-Graphic/Layout';

import {cols_to_rows, formatFigure} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';


const legend = {
  0: {
    title: "Pôles de proximité",
    subtitle: "école, médecin, commerce alimentaire",
    pattern: pattern_cluster_0
  },
  1: {
    title: "Pôles intermédiaires",
    subtitle: "restauration, infrastructures sportives ou culturelles, commerces et services",
    pattern: pattern_cluster_1
  },
  2: {
    title: "Pôles complets",
    subtitle: "tous commerces et services",
    pattern: pattern_cluster_2
  },
}


function getClusterLayer(objects, selected_filters, typology){
  let {modes} = selected_filters
  let {services_clusters} = objects

  let pt_legend = {
    pattern: legend[typology].pattern,
    title: legend[typology].title,
    subtitle: legend[typology].subtitle
  }

  let cluster_layer = new PointLayer({
    geojson: services_clusters,
    filter: (d) => d.properties.typology === typology,
    getLabel: (d) => `<u>${formatFigure(d.places_nb)} commerces et services :</u></br> ${d.places}`,
    pattern: legend[typology].pattern,
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
  layers = layers.concat(getClusterLayer(objects, selected_filters, 0))
  layers = layers.concat(getClusterLayer(objects, selected_filters, 1))
  layers = layers.concat(getClusterLayer(objects, selected_filters, 2))
  return layers
}



export const places_services_cluster = new Indicator({
    indicator: "places_services_cluster",
    label: "pôles de commerces et services",
    data_source: "computed",

    filters: [],

    tables: {},
    layers : {
      path: getAllLayer,
    },

    datasets_names: ["territory/services_cluster", "territory/gridded_pop"]
  })
