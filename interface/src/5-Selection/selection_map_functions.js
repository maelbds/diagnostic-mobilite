import * as d3 from "d3";
import booleanPointInPolygon from "@turf/boolean-point-in-polygon";

import {c_green_text as c_green, c_violet, c_blue} from "../a-Graphic/Colors"

import {delaunay_nextring} from "./utilities.js"

import {typo_map_color} from "./typo_aav.js"


export function buildCommunesLayer(context, projection, transform, communes_attr,
communes_sorted, epci, arrondissements, departements, select_by){

  const { width, height } = context.canvas.getBoundingClientRect();

  let path2154 = d3.geoPath(projection, context)

  let t2 = performance.now()

  context.save();
  context.clearRect(0, 0, width, height);
  context.translate(transform.x, transform.y);
  context.scale(transform.k, transform.k);

  // COMMUNES
  context.beginPath()
  context.lineWidth = 0.5/transform.k
  context.strokeStyle = "white"
  let last_typo

  for (let i = 0; i < communes_sorted.length; i++) {
    let c = communes_sorted[i]
    let typo = communes_attr.get(c.properties.codgeo).typo_aav

    if (typo !== last_typo) {
      context.fill()
      context.stroke()
      context.beginPath()
      context.fillStyle = typo_map_color.get(typo)
    }
    path2154(c)
    last_typo = typo
  }
  context.fill()
  context.stroke()


  if(select_by === "epci" | select_by === "com"){
    // EPCI
    context.beginPath()
    context.lineWidth = 0.85/transform.k
    context.strokeStyle = "#666"
    epci.features.forEach( d => {
      path2154(d)
      }
    )
    context.stroke()
  }

  if(select_by === "arr"){
    // ARRONDISSEMENTS
    context.beginPath()
    context.lineWidth = 0.85/transform.k
    context.strokeStyle = "#666"
    arrondissements.features.forEach( d => {
      path2154(d)
      }
    )
    context.stroke()
  }

  context.restore();

  //console.log(~~(performance.now() - t2) + ' ms')
}

export function buildNamesLayer(context, projection, transform, communes_attr,
communes_sorted, epci, arrondissements, departements, emd_added, emd_to_add, cheflieu_dep){

  const { width, height } = context.canvas.getBoundingClientRect();

  let path2154 = d3.geoPath(projection, context)

  let t2 = performance.now()

  context.save();
  context.clearRect(0, 0, width, height);
  context.translate(transform.x, transform.y);
  context.scale(transform.k, transform.k);


  // DEPARTEMENTS
  context.beginPath()
  context.lineWidth = 1/transform.k
  context.strokeStyle = "#333"
  departements.features.forEach( d => {
    path2154(d)
    }
  )
  context.stroke()

  // COMMUNES EMD
  if (transform.k > 3.5){
      context.beginPath()
      context.lineWidth = 5/transform.k
      context.strokeStyle = "white"
      path2154(emd_added)
      context.stroke()

      context.beginPath()
      context.lineWidth = 2.5/transform.k
      context.strokeStyle = c_violet
      path2154(emd_added)
      context.stroke()
  }
  if (transform.k > 3.5){
      context.beginPath()
      context.lineWidth = 5/transform.k
      context.strokeStyle = "white"
      context.lineCap = "round"
      context.setLineDash([2.5/transform.k * 4, 2.5/transform.k * 3])
      path2154(emd_to_add)
      context.stroke()

      context.beginPath()
      context.lineWidth = 2.5/transform.k
      context.strokeStyle = c_violet
      context.lineCap = "round"
      context.setLineDash([2.5/transform.k * 4, 2.5/transform.k * 3])
      path2154(emd_to_add)
      context.stroke()
  }

  context.restore();

  // names
  context.globalAlpha = 0.7
  context.font = "600 16px 'Source Sans Pro'"
  context.lineWidth = 1.5
  context.fillStyle = "white"
  context.strokeStyle = 'white'

  let transformName = d3.zoomIdentity.translate(transform.x, transform.y).scale(transform.k);

  cheflieu_dep.forEach(function(d) {
      let xy = transformName.apply(projection([+d.cheflieu_x, +d.cheflieu_y]))
      let m = context.measureText(d.name.replace('Saint','St'))
      context.fillRect(xy[0] - m.width/2, xy[1]-10, m.width, 10);
      context.strokeRect(xy[0] - m.width/2, xy[1]-10, m.width, 10);
    })

  context.globalAlpha = 1
  context.font = "400 16px 'Source Sans Pro'"
  context.lineWidth = 2
  context.lineCap  = "round"
  context.lineJoin = "round"
  context.fillStyle = "black"
  context.strokeStyle = 'white'
  context.textAlign = "center"

  cheflieu_dep.forEach(function(d) {
      let xy = transformName.apply(projection([+d.cheflieu_x, +d.cheflieu_y]))
      context.strokeText(d.name.replace('Saint','St'), xy[0], xy[1])
      context.fillText(d.name.replace('Saint','St'), xy[0], xy[1])
    })

  //console.log(~~(performance.now() - t2) + ' ms')
}


export function buildHoverLayer(context, projection, transform,
    communes_attr, epci_attr, dep_attr, arr_attr, aav_attr,
    epci_feature_by_code, arr_feature_by_code, dep_feature_by_code,
    delaunay, centroids,
    communes,
    select_by, updateSelectedCommunes, updateInfo, selected_regions){

  const { width, height } = context.canvas.getBoundingClientRect();

  let path2154 = d3.geoPath(projection, context)

  let j

  let move = (e) => {
    let ptMouse2154, l, testIn, j0, iter = 0
    const [x, y] = transform.invert(d3.pointer(e))
    j = j0 = delaunay.find(x, y, j)

    ptMouse2154 = projection.invert([x, y])
    testIn = booleanPointInPolygon(ptMouse2154, communes.features[j])

      if (!testIn) {
        let current_ring = [j], kernel = [], next_ring

        while ( l === undefined && iter++ < 4) {
          next_ring = delaunay_nextring(delaunay, current_ring, kernel)

          l = next_ring.find(k => booleanPointInPolygon(ptMouse2154, communes.features[k]))

          kernel = kernel.concat(current_ring)
          current_ring = next_ring
        }

        if (l !== undefined) j = l
        else {
          j = undefined
          context.clearRect(0, 0, width, height);
          updateInfo(null)
        }
      }

      if (j !== undefined && selected_regions.includes(communes_attr.get(communes.features[j].properties.codgeo).reg)) {
        let commune = communes.features[j]
        let code_commune = commune.properties.codgeo
        let code_epci = communes_attr.get(code_commune).epci,
            code_arr = communes_attr.get(code_commune).arr,
            code_dep = communes_attr.get(code_commune).dep,
            h_epci = epci_feature_by_code.get(code_epci),
            h_arr = arr_feature_by_code.get(code_arr),
            h_dep = dep_feature_by_code.get(code_dep)
        updateInfo(code_commune)

        context.save();
        context.clearRect(0, 0, width, height);
        context.translate(transform.x, transform.y);
        context.scale(transform.k, transform.k);

        // commune
        context.beginPath()
        context.strokeStyle = c_green
        context.lineWidth = 1.5/transform.k
        path2154(commune)
        context.stroke()

        // epci
        context.beginPath()
        context.strokeStyle = c_green
        context.lineWidth = 2.5/transform.k
        if(select_by === "epci"){
          path2154(h_epci)
        }else if(select_by === "arr"){
          path2154(h_arr)
        }else if(select_by === "dep"){
          path2154(h_dep)
        }
        context.stroke()


        context.restore()

        if (e.type === "click") {
          let new_c_selected_geo_code
          if (select_by === "epci") new_c_selected_geo_code = h_epci.properties.communes.map(c=>c.geo_code)
          else if (select_by === "arr") new_c_selected_geo_code = h_arr.properties.communes.map(c=>c.geo_code)
          else if (select_by === "dep") new_c_selected_geo_code = h_dep.properties.communes.map(c=>c.geo_code)
          else new_c_selected_geo_code = [code_commune]

          updateSelectedCommunes(new_c_selected_geo_code)
        }
      }
      else {
        updateInfo(null)
        context.clearRect(0, 0, width, height);
      }
  }
  d3.select("#map_layers").on("touchmove mousemove click", move)
  d3.select("#map_layers").on("mouseout", () => {
      updateInfo(null)
      context.clearRect(0, 0, width, height);
  })
}


export function buildSelectedCommunesLayer(context, projection, transform, com_feature_by_code, selected_communes){
  const { width, height } = context.canvas.getBoundingClientRect();

  let path2154 = d3.geoPath(projection, context)

  context.save();
  context.clearRect(0, 0, width, height);
  context.translate(transform.x, transform.y);
  context.scale(transform.k, transform.k);

  // DEPARTEMENTS
  context.beginPath()
  context.lineWidth = 1/transform.k
  context.strokeStyle = c_green
  context.fillStyle = c_green + "cc"
  selected_communes.forEach( c => {
    path2154(com_feature_by_code.get(c))
    }
  )
  context.fill()
  context.stroke()

  context.restore();
}
