import {Layer} from 'ol/layer.js';

import * as d3 from "d3";
import * as topojson from "topojson";

import {toLonLat} from 'ol/proj.js';
import {context2d} from '../utilities.js'

import {c_dark} from "../../a-Graphic/Colors";
import {strokeWidth} from '../../a-Graphic/Layout';


export class NamesLayer extends Layer {
  constructor(options) {
    super(options);

    this.mesh = options.mesh

    this.canvas =  d3.create("canvas").style('position', 'absolute').attr("class", "ol-layer allow_hover_layer").node();
  }

  getSourceState() {
    return 'ready';
  }

  updateMesh(options){
    this.mesh = options.mesh
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

    let d3Path = d3.geoPath().projection(d3Projection).context(context);

    let offset = [8, 0]

    context.beginPath()
    context.lineWidth = 4
    context.strokeStyle = "#ffffffe6"
    context.strokeOpacity = 0.8
    context.fillStyle = "black"
    context.textAlign = "center"
    context.lineCap  = "round"
    context.lineJoin = "round"
    context.font = "400 16px source sans pro"
    this.mesh.features.forEach((f) => {
      context.strokeText(f.properties.libgeo, ...d3Projection(f.properties.center).map((v, i) => v + offset[i]))
      context.fillText(f.properties.libgeo, ...d3Projection(f.properties.center).map((v, i) => v + offset[i]))
    });
    context.stroke()


    return this.canvas;
  }
}
