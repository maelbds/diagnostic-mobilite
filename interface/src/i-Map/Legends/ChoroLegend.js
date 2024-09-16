import * as d3 from "d3";

import {strokeWidth} from '../../a-Graphic/Layout'
import {c_yellow, c_missing_data} from '../../a-Graphic/Colors'

import {formatFigure} from '../../f-Utilities/util_func';
import {wrap} from '../utilities';

import {Legend, spacing, circle_range_max} from './Legend';


export class ChoroLegend extends Legend{
  constructor(options){
    super(options)
    this.options = options
  }

  addUnit(){}

  addSpecific(){
    let height_color = 20
    let offset_color = 25

    let {thresholds, colors, unit, format, no_data} = this.options

    let choro_element = this.legend_element.append("g").attr("transform", `translate(0, ${this.yOffset + 5})`)

    let rectangles = choro_element.append("g")
    rectangles.selectAll('rect')
            .data(colors)
            .enter().append('rect')
            .attr('x', 0).attr('y', (d, i) => i*offset_color)
            .attr("rx", 3).attr("ry", 3)
            .attr('width', circle_range_max * 2)
            .attr('height', height_color)
            .style('fill', (d) => d)
            .style('stroke', "white").style('stroke-width', strokeWidth)

    if (no_data){
        rectangles.append('rect')
                .attr('x', 0).attr('y', colors.length*offset_color)
                .attr("rx", 3).attr("ry", 3)
                .attr('width', circle_range_max * 2)
                .attr('height', height_color - 5)
                .style('fill', c_missing_data)
                .style('stroke', "white").style('stroke-width', strokeWidth)
    }

    let legends = choro_element.append('g')
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

      if (no_data){
          legends.append('text')
                  .attr('x', circle_range_max * 2 + spacing)
                  .attr('y', colors.length*offset_color + (height_color - 5)/2)
                  .attr('shape-rendering', 'crispEdges')
                  .style('text-anchor', 'start')
                  .attr('alignment-baseline', 'middle')
                  .style('fill', "black")
                  .attr('font-family', "source sans pro").attr('font-weight', "300").attr('font-size', "15px")
                  .text("indisponible")
      }

      this.yOffset += choro_element.node().getBBox().height + 5

      return choro_element
  }

}
