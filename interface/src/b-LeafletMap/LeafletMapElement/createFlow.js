import {c_gradient_reds} from '../../a-Graphic/Colors';

import {managePopup} from '../LeafletMapUtil/managePopup';
import {getRange, rangeToThresholds} from '../thresholds_functions';

import * as d3 from "d3";
import * as ss from "simple-statistics";

const L = window.L;

export function createFlowsLayer(coords, masses, labels, scale_mode="ckmeans", colors=c_gradient_reds){
      let [range, range_labels] = getRange(scale_mode, masses, colors.length)
      let thresholds = rangeToThresholds(range)
      let scale_color = d3.scaleThreshold()
                    .domain(thresholds)
                    .range(colors);
      let scale_width = d3.scaleThreshold()
                    .domain(thresholds)
                    .range(ss.equalIntervalBreaks([2, 14], colors.length-1));
      let scale_radius = d3.scaleThreshold()
            .domain(thresholds)
            .range(ss.equalIntervalBreaks([15, 40], colors.length-1));

      var flows_g = []
      for (let i=0; i<coords.length; i++){
        let flow;
        if(coords[i][0] != coords[i][1]){
          flow = L.polyline(coords[i], {
            color: scale_color(masses[i]),
            fillOpacity: 1,
            weight: scale_width(masses[i]),
            opacity: 1
          });}
        else{
          flow = L.circleMarker(coords[i][0], {
            radius: scale_radius(masses[i]),
            color: scale_color(masses[i]),
            fillOpacity: 0,
            weight: scale_width(masses[i]),
            opacity: 1
          });
        }
          if(labels!=null){
            managePopup(flow, "<p class='leaflet_map_popup'>" + labels[i] + "</p>");
          }
          flows_g.push(flow);
        }
      var flows_layer = L.featureGroup(flows_g);
      return flows_layer
    }
