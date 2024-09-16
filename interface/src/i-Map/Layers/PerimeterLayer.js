import {Layer} from 'ol/layer.js';

import * as d3 from "d3";
import * as topojson from "topojson";

import {toLonLat} from 'ol/proj.js';
import {context2d} from '../utilities.js'

import {c_dark} from "../../a-Graphic/Colors";


export class PerimeterLayer extends Layer {
  constructor(options) {
    super(options);
    this.perimeter = options.perimeter

    this.canvas =  d3.create("canvas").style('position', 'absolute').attr("class", "ol-layer").node();
  }

  getSourceState() {
    return 'ready';
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
    context.setLineDash([1.5, 4]);
    context.lineWidth = 1.5
    context.lineCap= "round"
    context.lineJoin = "round"
    context.strokeStyle = c_dark
    d3Path(this.perimeter)
    context.stroke()

    return this.canvas;
  }
}
