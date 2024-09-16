import {Layer} from 'ol/layer.js';

import * as d3 from "d3";
import * as topojson from "topojson";

import {toLonLat} from 'ol/proj.js';
import {context2d} from '../utilities.js'

import {c_dark} from "../../a-Graphic/Colors";
import {strokeWidth} from '../../a-Graphic/Layout';


export class MeshLayer extends Layer {
  constructor(options) {
    super(options);

    this.mesh_lines = options.mesh_lines
    this.mesh_outline = options.mesh_outline

    this.canvas =  d3.create("canvas").style('position', 'absolute').attr("class", "ol-layer").node();
  }

  getSourceState() {
    return 'ready';
  }

  updateMesh(options){
    this.mesh_lines = options.mesh_lines
    this.mesh_outline = options.mesh_outline
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

    context.beginPath()
    context.lineWidth = strokeWidth
    context.lineJoin = "round"
    context.strokeStyle = "white"
    d3Path(this.mesh_lines)
    d3Path(this.mesh_outline)
    context.stroke()


    return this.canvas;
  }
}
