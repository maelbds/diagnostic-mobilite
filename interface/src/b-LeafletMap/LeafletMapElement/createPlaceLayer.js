import {c_yellow} from '../../a-Graphic/Colors';

import {managePopup} from '../LeafletMapUtil/managePopup';

import * as d3 from "d3";
import * as ss from "simple-statistics";

const L = window.L;

export function createPlacesLayer(coords, s = 20, c = c_yellow, labels=null){
    var places_g = []
    for (var i=0; i<coords.length; i++){
      let place = L.circleMarker(coords[i],
        {
        radius: s,
        color: "#fff",
        fillColor: c,
        weight: 1.3, //1,
        opacity: 1, //0.9,
        fillOpacity: 1, //0.75,
      });
      if(labels!=null){
        managePopup(place, "<p class='leaflet_map_popup'>" + labels[i] + "</p>");
      }
      places_g.push(place);
    }
    var places_layer = L.featureGroup(places_g);
    return places_layer
}
