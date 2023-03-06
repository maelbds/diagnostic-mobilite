import {c_yellow} from '../../a-Graphic/Colors';

import {managePopup} from '../LeafletMapUtil/managePopup';

import * as d3 from "d3";
import * as ss from "simple-statistics";

const L = window.L;

export function createPointsMassLayer(coords, masses, labels=null, color=null){
    let scale = d3.scalePow().exponent(1/2)
              .domain([0, d3.max(masses)])
              .range([3, 30])

    var points_g = []
    for (var i=0; i<coords.length; i++){
      let point = L.circleMarker(coords[i],
        {
        radius: scale(masses[i]),
        color: "#fff",
        fillColor: color == null ? c_yellow : color,
        weight: 1.5, //1,
        opacity: 1, //0.9,
        fillOpacity: 1, //0.75,
      });
      if (labels != null){
        managePopup(point, "<p class='leaflet_map_popup'>" + labels[i] + "</p>");
      }
      points_g.push(point);
    }
    var points_layer = L.featureGroup(points_g);
    return points_layer
  }
