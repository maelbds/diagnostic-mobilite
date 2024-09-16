import {Layer} from 'ol/layer.js';

import * as d3 from "d3";

import {c_light} from '../../a-Graphic/Colors'


export class LegendLayer extends Layer {
    constructor(options) {
      super(options);

      this.widthLegend = options.widthLegend
      this.heightLegend = options.widthLegend
      this.marginLegend = options.marginLegend
      this.paddingLegend = options.paddingLegend
      this.spacingLegendElements = options.spacingLegendElements

      this.legend = d3.create("svg")
      .style('position', 'absolute')
      .attr("class", "ol-layer legend allow_hover_layer")
    }

    getSourceState() {
      return 'ready';
    }

    render(frameState) {
      this.widthMap = frameState.size[0];
      this.heightMap = frameState.size[1];
      return this.legend.node();
    }

    update(legends) {
      const width = this.widthMap
      const height = this.heightMap

      let margin = this.marginLegend
      let widthLegend = this.widthLegend
      let heightLegend = this.heightLegend
      let paddingLegend = this.paddingLegend
      let spacingLegendElements = this.spacingLegendElements

      let legend = this.legend

      // initialize
      legend.attr("width", width).attr("height", height)
      legend.selectAll("*").remove()

      // create container with top right position
      let legend_container = legend.append("g")
          .attr("class", "legend-container")
          .attr("width", widthLegend)
          .attr("transform", `translate(${width - (widthLegend + 2 * paddingLegend) - margin}, ${margin})`)

      let heights = [0]
      if (legends.length > 0){
        // background rectangle
        legend_container.append("rect")
            .attr("width", widthLegend + 2 * paddingLegend)
            .attr("rx", 5)
            .attr("ry", 5)
            .style("fill", c_light + "eb")
            .style("stroke", "white")
            .style("stroke-width", 1)

        // add legend elements
        legends.forEach((l) => {
          let legend_element = l.addTo(legend_container)
          heights.push(legend_element.node().getBBox().height)
        });
      }

      // set spacing between legend elements
      let spacing = new Array(heights.length).fill(spacingLegendElements)
      spacing[0] = paddingLegend
      spacing[spacing.length-1] = paddingLegend

      // set offset to legend elements
      let yOffset = d3.cumsum(heights.map((e, i) => e + spacing[i]))
      legend.selectAll(".legend_element").data(yOffset).attr("transform", (d) => `translate(${this.paddingLegend}, ${d})`)
      legend_container.select("rect").attr("height", yOffset[yOffset.length-1])
    }
  }
