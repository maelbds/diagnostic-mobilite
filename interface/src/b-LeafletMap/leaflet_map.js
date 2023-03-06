import {c_yellow} from '../a-Graphic/Colors';
import {c_light, c_background} from '../a-Graphic/Colors';
import {c_gradient_greens as gradient_greens, c_gradient_reds as gradient_reds} from '../a-Graphic/Colors';
import {wz_size} from '../a-Graphic/Layout';

import {managePopup} from './LeafletMapUtil/managePopup';

import {getRange, rangeToThresholds} from './thresholds_functions';

import * as d3 from "d3";
import * as ss from "simple-statistics";

const L = window.L;

// ----------------------------------   MY MAP   --------------------------------------


function getMyMap(id, scale = false, padding = 0.3, background = true, zoom=true, attribution=true){
  // To build Leaflet map element
  var mymap = L.map(id, {
    center: [49, 0],
    zoom: 8,
    zoomDelta: 0.75,
    zoomSnap: padding,
    attributionControl: attribution,
    zoomControl: zoom,
    scrollWheelZoom: false,
    fadeAnimation: false
  });

  if (background){
    var mapbox_grey = 'https://api.mapbox.com/styles/v1/maelb96/ckvgdgsew4o8514nzwt93grne/tiles/{z}/{x}/{y}?access_token={accessToken}';
    var mapbox_beige = 'https://api.mapbox.com/styles/v1/maelb96/ckuz6hglv0hwk14rs0kaxav3r/tiles/{z}/{x}/{y}?access_token={accessToken}';
    L.tileLayer(mapbox_beige, {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoibWFlbGI5NiIsImEiOiJjaWx6ZjhmOWEwMGhxdm1tNThxamljbmtiIn0.cTyK6__rQH7lhZntrQlhWg'
    }).addTo(mymap);
  }

  /*
  L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
    maxZoom: 20,
    attribution: '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(mymap);
  */

  // ---SCALE
  if (scale===true){
    L.control.scale().addTo(mymap);
  }
  return mymap
}


// --------------------------------   LEGEND  ----------------------------------------

function getLegendMode(mode, values, colors){
  let split_nb = colors.length
  let [range, range_labels] = getRange(mode, values, split_nb)
  return [range_labels, colors]
}






// OLD STUFF BELOW - IGNORE -----------------------------------------------------------------------------------------------------------------------------

// --------------------------------   UTILITIES  ----------------------------------------

function calcDist(coord1, coord2){
  let v = [coord1[0] - coord2[0], coord1[1] - coord2[1]]
  let conv_deg_km = [Math.PI / 180 * 6400, Math.PI / 180 * 4400]
  let v_conv = [v[0]*conv_deg_km[0], v[1]*conv_deg_km[1]]
  let crow_fly_dist = Math.sqrt(v_conv[0]**2 + v_conv[1]**2)
  // To estimate dist via road
  // From crow-fly distances to real distances, or the origin of detours, Heran"
  let dist = crow_fly_dist * (1.1 + 0.3 * Math.exp(-crow_fly_dist / 20))
  return dist
}
// --------------------------------   EPCI  ----------------------------------------

function createEPCILayer(map, epci_geojson, labels=null, color=c_yellow){
  let epci_g = [];
  for (var i=0; i<epci_geojson.length; i++){
    var e = epci_geojson[i]
      let epci = L.geoJSON(e, {
        color: "#fff",
        fillColor: color,
        weight: 1.5,
        opacity: 0.8,
        fillOpacity: 0.75,
      });
      if(labels!=null){
        managePopup(epci, "<p class='leaflet_map_popup'>" + labels[i] + "</p>");
      }
      epci_g.push(epci);
  }
  let communes_layer = L.featureGroup(epci_g);
  communes_layer.addTo(map);
  return communes_layer
}

// --------------------------------   RESIDENTIAL AREAS  ----------------------------------------

function createResidentialAreasMassLayer(map, residential_areas, masses=null, labels=null, scale_mode="ckmeans", colors=gradient_greens){
  let [range, range_labels] = getRange(scale_mode, masses, colors.length)
  let thresholds = rangeToThresholds(range)
  let scale = d3.scaleThreshold()
                .domain(thresholds)
                .range(colors);

  let r_areas = [];
  for (var i=0; i<residential_areas.length; i++){
    let ra = residential_areas[i]
    let color_ra;
    if (masses != null){
      color_ra = scale(masses[i])
    } else {
      color_ra = c_light
    }
    let r_area = L.polygon(ra.outline, {
        color: color_ra,
        fillOpacity: 1,
        weight: 2,
        opacity: 1
      });

    if(labels != null){
      managePopup(r_area, "<p class='leaflet_map_popup'>" + labels[i] + "</p>");
    }
    r_areas.push(r_area);
  }
  let r_areas_layer = L.featureGroup(r_areas);
  r_areas_layer.addTo(map);
  return r_areas_layer//, hab_limit1, hab_limit2
}

function createResidentialAreasWhiteZoneLayer(map, residential_areas, wz_coords, distances, limit1=1.5, limit2=5, colors=gradient_reds){
  let wz_areas = [];
  let hab_limit1 = 0;
  let hab_limit2 = 0;

  for (var i=0; i<residential_areas.length; i++){
    let ra = residential_areas[i]
    let min_dist_areas = Math.min(...wz_coords.map((wz) => calcDist(ra.coords, wz)))
    let color_wz = min_dist_areas > limit2 ? colors[3] : (min_dist_areas > limit1 ? colors[1] : "transparent")

    let wz_area = L.circleMarker(ra.coords, {
      radius: wz_size,
      color: color_wz,
      fillColor: color_wz,
      fillOpacity: 0.15,
      weight: 0,
      opacity: 1
    });
    wz_areas.push(wz_area);
  }
  let wz_areas_layer = L.featureGroup(wz_areas);
  wz_areas_layer.addTo(map);
  return wz_areas_layer//, hab_limit1, hab_limit2
}





export default getMyMap;

export {
  calcDist,
  createResidentialAreasMassLayer, createResidentialAreasWhiteZoneLayer,
  createEPCILayer,

  getLegendMode
};
