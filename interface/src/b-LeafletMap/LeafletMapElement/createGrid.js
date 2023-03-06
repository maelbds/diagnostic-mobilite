import {c_light, c_gradient_greens} from '../../a-Graphic/Colors';

import {managePopup} from '../LeafletMapUtil/managePopup';
import {getRange, rangeToThresholds} from '../thresholds_functions';

import * as d3 from "d3";
import * as ss from "simple-statistics";

const L = window.L;

export function createGridLayer(coords, masses, labels=null, scale_mode="ckmeans", colors=c_gradient_greens){
  let [range, range_labels] = getRange(scale_mode, masses, colors.length)
  let thresholds = rangeToThresholds(range)
  let scale = d3.scaleThreshold()
                .domain(thresholds)
                .range(colors);

    var areas_g = []
    for (var i=0; i<coords.length; i++){
      let area = L.circle(coords[i],
        {
        radius: 100,
        color: "#fff",
        fillColor: scale(masses[i]),
        weight: 0, //1,
        opacity: 1, //0.9,
        fillOpacity: 1, //0.75,
      });
      if (labels != null){
        managePopup(area, "<p class='leaflet_map_popup'>" + labels[i] + "</p>");
      }
      areas_g.push(area);
    }
    var areas_layer = L.featureGroup(areas_g);
    return areas_layer
  }
