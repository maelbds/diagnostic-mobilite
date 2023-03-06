import {c_gradient_greens} from '../../a-Graphic/Colors';
import {pattern_dedicated_cycle_paths} from '../../a-Graphic/Layout';

import {managePopup} from '../LeafletMapUtil/managePopup';

const L = window.L;

export function createCyclePath(paths_geojson, labels=null, pattern=pattern_dedicated_cycle_paths){
  var cycle_paths_g = []
  for (var i=0; i<paths_geojson.length; i++){
      let cycle_path = L.geoJSON(paths_geojson[i], {
        color: pattern.color,
        fillOpacity: 1,
        lineCap: "round",
        dashArray: pattern.dashArray,
        weight: pattern.width,
        opacity: 1
      });
      if(labels!=null){
        managePopup(cycle_path, "<p class='leaflet_map_popup'>" + labels[i] + "</p>");
      }
      cycle_paths_g.push(cycle_path);
    }
  var cycle_paths_layer = L.featureGroup(cycle_paths_g);
  return cycle_paths_layer
}
