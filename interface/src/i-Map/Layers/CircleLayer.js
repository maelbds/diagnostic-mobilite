import {Layer} from 'ol/layer.js';

import * as d3 from "d3";

import {toLonLat} from 'ol/proj.js';
import {context2d} from '../utilities.js'

import {c_yellow, c_violet} from '../../a-Graphic/Colors'
import {strokeWidth} from '../../a-Graphic/Layout'

import {CircleLegend} from '../Legends/CircleLegend'
import {layers_z_index} from '../map_z_index'

const Plot = window.Plot


export class CircleLayer extends Layer {
    constructor(options) {
      super(options);
      let {geojson, getValue, getLabel, legend} = options;

      // set mesh labels to display on hover
      this.mesh_labels = new Map(geojson.features.map((f) => [f.properties.codgeo, getLabel(f.properties)]))

      // sort elements with data | no data
      let wd_elements = this.wd_elements = geojson.features.filter((f) => getValue(f.properties) !== undefined)
      let nd_elements = this.nd_elements = geojson.features.filter((f) => getValue(f.properties) === undefined)

      // set geosjon to display
      let centers = this.centers = {type: "FeatureCollection", features: wd_elements.map((f) => ({
          type: "Feature",
          properties: {
            value: getValue(f.properties)
          },
          geometry: {
            type: "Point",
            coordinates: f.properties.center
          }
        }))}

      // set legend
      this.legend = new CircleLegend({
        domain: [d3.min(wd_elements.map((f) => getValue(f.properties))), d3.max(wd_elements.map((f) => Math.abs(getValue(f.properties))))],
        range: [0, 25],
        ...legend
      })

      this.svg = d3.create("svg")
      .style('position', 'absolute')
      .attr("class", "ol-layer")
      .style("pointer-events", "none")
      .node();
      this.init = true
      this.z_index = layers_z_index.circleLayer
    }

    getSourceState() {
      return 'ready';
    }

    render(frameState) {
      if (this.init){
        this.postrender(frameState)
        this.init = false
      }
      return this.svg;
    }

    prerender(frameState) {
      d3.select(this.svg).selectAll("*").remove();
    }

    postrender(frameState) {
      const width = frameState.size[0];
      const height = frameState.size[1];

      let center = toLonLat(frameState.viewState.center)
      let scale = Math.pow(2, 8 + frameState.viewState.zoom ) / (2 * Math.PI)
      const angle = (-frameState.viewState.rotation * 180) / Math.PI;

      const d3Projection = d3.geoMercator()
        .scale(scale)
        .center(center)
        .translate([width / 2, height / 2])
        .angle(angle);

      const d3Path = d3.geoPath(d3Projection)

      let new_svg = Plot.plot({
        inset: 0,
        width: width,
        height: height,
        projection: {
          type: () => d3Projection
        },
        r: {range: [0, 25]},
        marks: [
            Plot.geo(this.centers, {
              r: (d) => Math.abs(d.properties.value),
              fill: (d) => d.properties.value < 0 ? c_violet : c_yellow,
              fillOpacity: 1,
              stroke: "white",
              strokeWidth: strokeWidth
            })
          ]
      })
      new_svg.style = `position: absolute; pointer-events: none;`

      d3.select(this.svg).node().replaceWith(new_svg)
      this.svg = new_svg
    }
  }
