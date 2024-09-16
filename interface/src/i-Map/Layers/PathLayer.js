import { Layer } from "ol/layer.js";

import * as d3 from "d3";

import { toLonLat } from "ol/proj.js";

import { PathLegend } from "../Legends/PathLegend";
import {layers_z_index} from '../map_z_index'

const Plot = window.Plot;

export class PathLayer extends Layer {
  constructor(options) {
    super(options);

    this.geojson = options.geojson;
    this.filter = options.filter;
    this.getLabel = options.getLabel;
    this.pattern = options.pattern;

    this.allLabels = this.geojson.features.filter(this.filter).map(f => this.getLabel(f.properties))

    // set legend
    this.legend = new PathLegend({
      ...options.legend
    })

    this.svg = d3
      .create("svg")
      .style("position", "absolute")
      .attr("class", "ol-layer")
      .style("pointer-events", "none");
    this.init = false;
    this.z_index = layers_z_index.pathLayer
  }

  getSourceState() {
    return "ready";
  }

  render(frameState) {
    if (!this.init) {
      this.postrender(frameState);
      this.init = true;
    }
    return this.svg.node();
  }

  prerender(frameState) {
    this.svg.selectAll("*").remove();
  }

  postrender(frameState, popup) {
    const width = frameState.size[0];
    const height = frameState.size[1];

    let center = toLonLat(frameState.viewState.center);
    let scale = Math.pow(2, 8 + frameState.viewState.zoom) / (2 * Math.PI);
    const angle = (-frameState.viewState.rotation * 180) / Math.PI;

    const d3Projection = d3
      .geoMercator()
      .scale(scale)
      .center(center)
      .translate([width / 2, height / 2])
      .angle(angle);

    const d3Path = d3.geoPath(d3Projection);

    // initialize
    this.svg.attr("width", width).attr("height", height);
    this.svg.selectAll("*").remove();

    this.svg.selectAll()
      .data(this.geojson.features.filter(this.filter))
      .join((enter) => {
        let g = enter.append('g')
        .attr("fill", "none")
        .attr("stroke-linecap", "round")
        .attr("stroke-linejoin", "round")

        if (this.pattern.whiteOutline){
          g.append('path')
            .attr("d", d3Path)
            .attr("stroke", "white")
            .attr("stroke-width", this.pattern.strokeWidth + 2)
            .style("pointer-events", "stroke");
        }

        g.append('path')
          .attr("d", d3Path)
          .attr("stroke", (d, i) => this.pattern.colors[i%this.pattern.colors.length])
          .attr("stroke-width", this.pattern.strokeWidth)
          .attr("stroke-dasharray", this.pattern.strokeDasharray)
          .style("pointer-events", "stroke");

        return g;
      })
  }

  addHover(popup) {
    function onMouseMove(e){
      e.currentTarget.popup.show(e, `${e.currentTarget.label}`);
    }
    function onMouseOut(e){
      popup.hide()
    }

    this.svg
      .selectAll("g")
      .nodes()
      .forEach((item, i) => {
        item.label = this.allLabels[i]
        item.popup = popup
        item.addEventListener("mousemove", onMouseMove)
      });

    this.svg.selectAll("g").on("mouseout", onMouseOut);
  }
}
