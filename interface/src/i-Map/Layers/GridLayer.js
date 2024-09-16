import {Layer} from 'ol/layer.js';

import * as d3 from "d3";

import {toLonLat} from 'ol/proj.js';

import {c_yellow, c_light} from '../../a-Graphic/Colors'

import {GridLegend} from '../Legends/GridLegend'
import {layers_z_index} from '../map_z_index'


const Plot = window.Plot


export class GridLayer extends Layer {
    constructor(options) {
      super(options);

      this.grid = options.grid
      this.getValue = options.getValue
      this.getLabel = options.getLabel
      //this.legend = options.legend

      this.allLabels = this.grid.features.map(f => this.getLabel(f.properties))


      let scale = this.scale = d3.scaleThreshold()
                  .domain(options.legend.thresholds.slice(1, -1))
                  .range(options.legend.colors);


      // set legend
      this.legend = new GridLegend({
        ...options.legend
      })

      this.svg = d3.create("svg")
      .style('position', 'absolute')
      .attr("class", "ol-layer")
      .style("pointer-events", "none");
      this.init = false;
      this.z_index = layers_z_index.gridLayer
    }

    getSourceState() {
      return 'ready';
    }

    render(frameState) {
      if(!this.init){
        this.postrender(frameState)
        this.init = true
      }
      return this.svg.node()
    }

    prerender(frameState){
      this.svg.selectAll("*").remove();
    }

    postrender(frameState, popup){
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

      const point_grid_coords = this.grid.features[0].geometry.coordinates
      const d3Path = d3.geoPath(d3Projection)
      const grid_length_meter = 190 / 2
      const earth_radius_meter = 6371000
      const grid_radius_pixel = d3Path.measure({type: "LineString", coordinates: [point_grid_coords, [point_grid_coords[0], point_grid_coords[1] + grid_length_meter / earth_radius_meter * 180 /  Math.PI]]})

      // initialize
      /*this.svg.attr("width", width).attr("height", height)
      this.svg.selectAll("*").remove()

      this.svg.append("g")
              .selectAll('circle')
              .data(this.centers.features)
              .enter().append('circle')
              .attr("cx", (d) => d3Projection(d.properties.coords)[0])
              .attr("cy", (d) => d3Projection(d.properties.coords)[1])
              .attr("r", grid_radius_pixel)*/


      let new_svg = Plot.plot({
        inset: 0,
        width: width,
        height: height,
        projection: {
          type: () => d3Projection
        },
        r: { range: [grid_radius_pixel, grid_radius_pixel]}, // for gridded data only

        marks: [
            Plot.geo(this.grid, {
              r: (d) => 1,
              fill: (d) => this.scale(this.getValue(d.properties)),
              fillOpacity: 1,
              strokeWidth: 0,
              pointerEvents: "fill"
            }),
          ]
      })
      new_svg.style = `position: absolute;`

      this.svg.node().replaceWith(new_svg)
      this.svg = d3.select(new_svg)
    }

    addHover(popup){
      function onMouseMove(e){
        e.currentTarget.popup.show(e, `<b>${e.currentTarget.label}</b>`);
      }
      function onMouseOut(e){
        popup.hide()
      }

      this.svg.selectAll("path").nodes().forEach((item, i) => {
        item.label = this.allLabels[i]
        item.popup = popup
        item.addEventListener("mousemove", onMouseMove)
      });

      this.svg.selectAll("path").on("mouseout", onMouseOut)
    }
  }
