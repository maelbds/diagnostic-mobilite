import {pattern_routes_pt, pattern_stops_pt, pattern_train_stations, pattern_railways} from '../a-Graphic/Layout';

import {PathLayer} from '../i-Map/Layers/PathLayer';
import {PointLayer} from '../i-Map/Layers/PointLayer';


import {cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';
import {PTModesFilter} from '../h-Filters/PTModesFilter'

var modes_filter = PTModesFilter.labels


const modes_types = {
  "train": [2],
  "metro": [1],
  "tram": [0],
  "bus": [3],
  "autre": [4, 5, 6, 7, 715, 8, 9, 10, 11, 12, 13, 14, 15, 16],
}


function filter_pt(filter_codes, d){
  let n = d.properties.route_name.toLowerCase()
  let is_not_tad = !n.includes(" tad ") && !n.includes("tad -") && !n.toLowerCase().includes("tad2 -") && !n.includes("transport à la demande")
  let is_not_long_distance = !n.includes("flixbus") && !n.includes("blablabus") && !n.toLowerCase().includes("blablacar")

  let is_selected_mode = filter_codes.includes(d.properties.route_type)

  return is_not_tad && is_not_long_distance && is_selected_mode
}

function getPTRoutesLayer(objects, selected_filters){
  let {modes} = selected_filters
  let {stops, routes} = objects

  let filter_codes = [].concat(modes.map((m) => modes_types[m])).flat()

  let pt_legend = {
    pattern: pattern_routes_pt,
    title: `Transports en commun`
  }

  let path_layer = new PathLayer({
    geojson: routes,
    filter: (d) => filter_pt(filter_codes, d),
    getLabel: (d) => `<u>Ligne :</u> ${d.route_name}`,
    pattern: pattern_routes_pt,
    legend: pt_legend,

  });

  return [path_layer]
}

function getRailwaysLayer(objects, selected_filters){
  let {modes} = selected_filters
  let {railways} = objects

  if (modes.includes("train")){
    let pt_legend = {
      pattern: pattern_railways,
      title: `Voie ferrée`
    }

    let path_layer = new PathLayer({
      geojson: railways,
      filter: (d) => true,
      getLabel: (d) => `<u>Voie ferrée :</u> ${d.name}`,
      pattern: pattern_railways,
      legend: pt_legend,

    });

    return [path_layer]
  } else {
    return []
  }
}

function getPTStopsLayer(objects, selected_filters){
  let {modes} = selected_filters
  let {stops, routes} = objects

  let filter_codes = [].concat(modes.map((m) => modes_types[m])).flat()

  let pt_legend = {
    pattern: pattern_stops_pt,
    title: `Points d'arrêt`
  }

  let stops_layer = new PointLayer({
    geojson: stops,
    filter: (d) => filter_pt(filter_codes, d),
    getLabel: (d) => `<u>Arrêt :</u> ${d.stop_name}`,
    pattern: pattern_stops_pt,
    legend: pt_legend,

  });

  return [stops_layer]
}

function getTrainStationsLayer(objects, selected_filters){
  let {modes} = selected_filters
  let {train_stations} = objects

  if (modes.includes("train")){
    let pt_legend = {
      pattern: pattern_train_stations,
      title: `Gares SNCF`
    }

    let stops_layer = new PointLayer({
      geojson: train_stations,
      filter: (d) => true,
      getLabel: (d) => `<u>Gare SNCF :</u> ${d.name}`,
      pattern: pattern_train_stations,
      legend: pt_legend,

    });

    return [stops_layer]
  } else {
    return []
  }
}

function getPTLayer(objects, selected_filters){
  let layers = []
  layers = layers.concat(getRailwaysLayer(objects, selected_filters))
  layers = layers.concat(getPTRoutesLayer(objects, selected_filters))
  layers = layers.concat(getPTStopsLayer(objects, selected_filters))
  layers = layers.concat(getTrainStationsLayer(objects, selected_filters))
  return layers
}

function getElementsTable(objects, selected_filters){
  let headlines = [], cols = [], format_table = [], format_csv = [], align = [];
  let {routes, railways} = objects
  let {modes} = selected_filters

  let filter_codes = [].concat(modes.map((m) => modes_types[m])).flat()

  headlines.push("Ligne")
  cols.push(routes.features.filter((d) => filter_pt(filter_codes, d)).map((f)=> f.properties.route_name))
  format_table.push((f)=>f)
  format_csv.push((f)=>f)
  align.push("l")

  return {headlines, cols, format_table, format_csv, align}
}


export const public_transport = new Indicator({
    indicator: "public_transport",
    label: "transports en commun",

    filters: [PTModesFilter],

    tables: {
      elements: getElementsTable
    },
    layers : {
      path: getPTLayer,
    },

    datasets_names: ["offer/public_transport", "offer/train_stations", "offer/railways"]
  })
