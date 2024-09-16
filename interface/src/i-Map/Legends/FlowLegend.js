import * as d3 from "d3";

import {strokeWidth} from '../../a-Graphic/Layout'
import {c_yellow, c_missing_data} from '../../a-Graphic/Colors'

import {formatFigure} from '../../f-Utilities/util_func';
import {wrap} from '../utilities';

import {Legend, spacing, circle_range_max} from './Legend';


export class FlowLegend extends Legend{
  constructor(options){
    super(options)
    this.options = options
  }

  addUnit(){}

  addSpecific(){
    let height_color = 20
    let offset_color = 25

    let {thresholds, colors, strokes, unit, format} = this.options

    let flow_element = this.legend_element.append("g").attr("transform", `translate(0, ${this.yOffset + 5})`)

    let lines_b = flow_element.append("g")
    lines_b.selectAll('path')
            .data(colors)
            .enter().append('path')
            .attr('d', (d, i) => {
              let arrow_head = strokes[i] * 2
              let angle = strokes[i] * 1/3
              return `M0,${height_color/2 + offset_color * i}Q${circle_range_max},${offset_color * i - height_color/2},${circle_range_max*2},${height_color/2 + offset_color * i}l-${angle},-${arrow_head}m${angle},${arrow_head}l-${arrow_head},${angle}`
              })
            .style('stroke', "white")
            .style('stroke-width', (d, i) => strokes[i] + 1)
            .attr("fill", "none")
            .attr("stroke-linecap", "round")
            .attr("stroke-linejoin", "round")

    let lines = flow_element.append("g")
    lines.selectAll('path')
            .data(colors)
            .enter().append('path')
            .attr('d', (d, i) => {
              let arrow_head = strokes[i] * 2
              let angle = strokes[i] * 1/3
              return `M0,${height_color/2 + offset_color * i}Q${circle_range_max},${offset_color * i - height_color/2},${circle_range_max*2},${height_color/2 + offset_color * i}l-${angle},-${arrow_head}m${angle},${arrow_head}l-${arrow_head},${angle}`
              })
            .style('stroke', (d) => d)
            .style('stroke-width', (d, i) => strokes[i])
            .attr("fill", "none")
            .attr("stroke-linecap", "round")
            .attr("stroke-linejoin", "round")

    let legends = flow_element.append('g')
    legends.selectAll('text')
          .data(thresholds.slice(0, -1))
          .enter().append('text')
          .attr('x', circle_range_max * 2 + spacing)
          .attr('y', (d, i) => offset_color * i + height_color/2)
          .attr('shape-rendering', 'crispEdges')
          .style('text-anchor', 'start')
          .attr('alignment-baseline', 'middle')
          .style('fill', "black")
          .attr('font-family', "source sans pro").attr('font-weight', "300").attr('font-size', "15px")
          .text((d, i) => `${format(thresholds[i])} à ${format(thresholds[i+1])} ${unit}`)

      this.yOffset += flow_element.node().getBBox().height + 5

      return flow_element
  }

}
