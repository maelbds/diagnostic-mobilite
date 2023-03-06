import {pattern_zfe} from '../../a-Graphic/Layout';

import {managePopup} from '../LeafletMapUtil/managePopup';

const L = window.L;

export function createZFE(path_geojson, label=null, pattern=pattern_zfe){
  var cycle_paths_g = []

  let cycle_path = L.geoJSON(path_geojson, {
    color: pattern.color,
    fill: false,
    lineCap: "round",
    dashArray: pattern.dashArray,
    weight: pattern.width,
    opacity: 1
  });
  if(label!=null){
    managePopup(cycle_path, "<p class='leaflet_map_popup'>" + label + "</p>");
  }
  cycle_paths_g.push(cycle_path);

  var cycle_paths_layer = L.featureGroup(cycle_paths_g);
  return cycle_paths_layer
}
