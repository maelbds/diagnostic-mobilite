import {c_light, c_gradient_greens, c_missing_data} from '../../a-Graphic/Colors';

import {managePopup} from '../LeafletMapUtil/managePopup';
import {getRange, rangeToThresholds} from '../thresholds_functions';

import {getLegendMode} from '../../b-LeafletMap/leaflet_map';

import * as d3 from "d3";
import * as ss from "simple-statistics";

const L = window.L;

export function createCommunesLayer(communes, labels=null, color=c_light){
  let communes_g = [];
  for (var i=0; i<communes.length; i++){
    var c = communes[i]
    for (let o of c.outline){
      let commune = L.polygon(o, {
        color: "#fff",
        fillColor: color,
        weight: 1.5,
        opacity: 0.8,
        fillOpacity: 0.8,
      });
      if(labels!=null){
        managePopup(commune, "<p class='leaflet_map_popup'>" + labels[i] + "</p>");
      }
      communes_g.push(commune);
    }
  }
  let communes_layer = L.featureGroup(communes_g);
  return communes_layer
}


export function createCommunesMassLayer(communes, masses, labels=null, scale_mode="ckmeans", colors=c_gradient_greens){
  let [range, range_labels] = getRange(scale_mode, masses, colors.length)
  let thresholds = rangeToThresholds(range)
  let scale = d3.scaleThreshold()
                .domain(thresholds)
                .range(colors);

  let communes_g = [];
  for (var i=0; i<communes.length; i++){
    var color_commune = scale(masses[i])
    for (let o of communes[i].outline){
      let commune = L.polygon(o, {
        color: "#fff",
        fillColor: color_commune,
        weight: 1.5,
        opacity: 0.85,
        fillOpacity: 0.8,
      });
      if(labels!=null){
        managePopup(commune, "<p class='leaflet_map_popup'>" + labels[i] + "</p>");
      }
      communes_g.push(commune);
    }
  }
  let communes_layer = L.featureGroup(communes_g);
  return communes_layer
}

export function createCommuneBordersLayer(communes){
  let communes_g = [];
  for (let c of communes){
    for (let o of c.outline){
      let commune = L.polygon(o, {
        color: "#fff",
        fillColor: c_light,
        weight: 1.5,
        opacity: 1,
        fillOpacity: 0.4,
      });
      communes_g.push(commune);
    }
  }
  let communes_layer = L.featureGroup(communes_g);
  return communes_layer
}


export function getCommunesMassElements(communes, p){
    let communes_wd = communes.filter((c) => p.indicatorFunction(c) != null)
    let communes_masses = communes_wd.map(p.massFunction);
    let communes_labels = communes_wd.map(p.labelFunction);

    let communes_nd = communes.filter((c) => p.indicatorFunction(c) == null)
    let communes_nd_labels = communes_nd.map((c) => c.name);

    let mode = p.mode
    let legend_label = p.legend_label
    let legend_unit = p.legend_unit
    let colors = p.colors
    let sources = p.sources

    let communes_layer = createCommunesMassLayer(communes_wd, communes_masses, communes_labels, mode, colors);
    let communes_layer_nd = createCommunesLayer(communes_nd, communes_nd_labels, c_missing_data);

    let legend_values = communes_masses
    let missing_data = communes_nd.length > 0

    let [legend_intervals, legend_colors] = getLegendMode(mode, legend_values, colors)
    var legend = [
      {type: "LegendLabel", params: {label: legend_label, unit: legend_unit}},
      {type: "LegendValues", params: {intervals: legend_intervals, colors: legend_colors, missing_data: missing_data}}
    ]

    let layer_to_fit = communes_layer.addLayer(communes_layer_nd)
    let layers = [communes_layer, communes_layer_nd]

    return {layer_to_fit, layers, legend, sources}
}
