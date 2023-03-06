import {c_gradient_reds} from '../../a-Graphic/Colors';

import {managePopup} from '../LeafletMapUtil/managePopup';

const L = window.L;

export function createRoutesLayer(routes, labels=null, w=2, colors=c_gradient_reds){
    let routes_g = []
    for (let i=0; i<routes.length; i++){
        let route = L.polyline(routes[i], {
          color: "white",
          fillOpacity: 1,
          lineCap: "butt",
          weight: w+3,
          opacity: 1
        });
        let route2 = L.polyline(routes[i], {
          color: colors[i%(colors.length)],
          fillOpacity: 1,
          weight: w,
          lineCap: "butt",
          opacity: 1
        });
        if(labels!=null){
          managePopup(route2, "<p class='leaflet_map_popup'>" + labels[i] + "</p>");
        }
        routes_g.push(route);
        routes_g.push(route2);
      }
    let routes_layer = L.featureGroup(routes_g);
    return routes_layer
  }
