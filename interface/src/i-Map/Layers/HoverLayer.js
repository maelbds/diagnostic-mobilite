import {Layer} from 'ol/layer.js';

import * as d3 from "d3";
import * as topojson from "topojson";
import booleanPointInPolygon from "@turf/boolean-point-in-polygon";


import {toLonLat} from 'ol/proj.js';


import {c_orange as c_hover} from "../../a-Graphic/Colors";
import {context2d, delaunay_nextring} from '../utilities.js'


export class HoverLayer extends Layer {
  constructor(geojson) {
    super(geojson);
    this.geojson = geojson

    // to identify communes when flying over map
    let path = d3.geoPath(d3.geoIdentity())
    let centroids = this.geojson.features.map(f => path.centroid(f))
    this.delaunay = d3.Delaunay.from(centroids)

    this.canvas =  d3.create("canvas").style('position', 'absolute').attr("class", "ol-layer allow_hover_layer").node();

    this.mesh_labels=[]
  }

  getSourceState() {
    return 'ready';
  }

  updateLabels(labels){
    this.labels = labels
  }

  updateMesh(geojson){
    this.geojson = geojson
    // to identify communes when flying over map
    let path = d3.geoPath(d3.geoIdentity())
    let centroids = geojson.features.map(f => path.centroid(f))
    this.delaunay = d3.Delaunay.from(centroids)
  }

  onHover(e, elements){
    let {frameState, popup} = elements
    let j, j0, l, testIn, iter = 0
    let projection = this.projection
    let delaunay = this.delaunay

    const [x, y] = projection.invert(d3.pointer(e))

    j = j0 = delaunay.find(x, y, j)

    testIn = booleanPointInPolygon([x, y], this.geojson.features[j])

      if (!testIn) {
        let current_ring = [j], kernel = [], next_ring

        while (l === undefined && iter++ < 4) {
          next_ring = delaunay_nextring(delaunay, current_ring, kernel)
          l = next_ring.find(k => booleanPointInPolygon([x, y], this.geojson.features[k]))
          kernel = kernel.concat(current_ring)
          current_ring = next_ring
        }

        if (l !== undefined) j = l
        else {
          j = undefined
        }
      }

      if (j !== undefined) {
          let hovered = this.geojson.features[j]
          let label = `<b><span className="mb-1">${hovered.properties.libgeo} - ${hovered.properties.codgeo}</span></b></br>`
          this.mesh_labels.forEach((l) => {
            label += `${l.get(hovered.properties.codgeo)}</br>`
          });

          //document.getElementById("info").innerHTML = hovered.properties.libgeo + " - " + hovered.properties.codgeo
          popup.show(e, label)
          this.render_hover(frameState, hovered)
      }
      else {
        //document.getElementById("info").innerHTML = "Balayer la carte"
        this.render_clean_hover(frameState)
        popup.hide()
      }
  }

  hide(){
    const width = 1000;
    const height = 1000;

    let context = context2d(this.canvas, width, height)
    context.clearRect(0, 0, width, height);
  }

  render(frameState) {
    const width = frameState.size[0];
    const height = frameState.size[1];

    let context = context2d(this.canvas, width, height)

    let center = toLonLat(frameState.viewState.center)
    let scale = Math.pow(2, 8 + frameState.viewState.zoom ) / (2 * Math.PI)
    const angle = (-frameState.viewState.rotation * 180) / Math.PI;

    const d3Projection = this.projection = d3.geoMercator()
      .scale(scale)
      .center(center)
      .translate([width / 2, height / 2])
      .angle(angle);

    return this.canvas;
  }

  render_hover(frameState, element) {
    const width = frameState.size[0];
    const height = frameState.size[1];

    let context = context2d(this.canvas, width, height)

    let center = toLonLat(frameState.viewState.center)
    let scale = Math.pow(2, 8 + frameState.viewState.zoom ) / (2 * Math.PI)
    const angle = (-frameState.viewState.rotation * 180) / Math.PI;

    const d3Projection = this.projection = d3.geoMercator()
      .scale(scale)
      .center(center)
      .translate([width / 2, height / 2])
      .angle(angle);

    let d3Path = d3.geoPath().projection(d3Projection).context(context);

    context.beginPath()
    context.lineWidth = 2
    context.fillStyle = c_hover + "12"
    context.strokeStyle = c_hover
    context.lineCap= "round"
    context.lineJoin = "round"
    d3Path(element)

    context.fill()
    context.stroke()
  }

  render_clean_hover(frameState){
    const width = frameState.size[0];
    const height = frameState.size[1];

    let context = context2d(this.canvas, width, height)
    context.clearRect(0, 0, width, height);
  }
}
