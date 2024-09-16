import * as d3 from "d3";

import {strokeWidth} from '../../a-Graphic/Layout'
import {c_yellow} from '../../a-Graphic/Colors'

import {formatFigure} from '../../f-Utilities/util_func';
import {wrap} from '../utilities';

import {Legend, spacing, circle_range_max} from './Legend';


export class PointLegend extends Legend{
  constructor(options){
    super(options)
    this.options = options
  }

  addTitle(){}

  addSubTitle(){}

  addUnit(){}

  addSpecific(){
    let height = 20

    let {pattern, title, subtitle} = this.options

    let point_element = this.legend_element.append("g").attr("transform", `translate(0, ${this.yOffset})`)

    point_element.append('circle')
              .attr('cx', circle_range_max).attr("cy", height/2)
              .attr("r", pattern.radius)
              .attr('stroke', "white")
              .attr("stroke-width", 1)
              .attr('fill', pattern.color)

    let title_element = point_element.append('text')
          .attr('x', circle_range_max * 2 + spacing).attr("y", height/2).attr("dy", "0.3em")
          .attr('shape-rendering', 'crispEdges')
          .style('text-anchor', 'start')
          .style('fill', "black")
          .attr('font-family', "source sans pro").attr('font-weight', "400").attr('font-size', "17px")
          .text(title)
          .call(wrap, this.width - 2*circle_range_max - spacing)

    if (subtitle !== null){
      let subtitle_element = point_element.append('text')
            .attr('x', circle_range_max * 2 + spacing).attr("y", title_element.node().getBBox().height + 8).attr("dy", "0.3em")
            .attr('shape-rendering', 'crispEdges')
            .style('text-anchor', 'start')
            .style('fill', "black")
            .attr('font-family', "source sans pro").attr('font-weight', "300").attr('font-size', "15px")
            .text(subtitle)
            .call(wrap, this.width - 2*circle_range_max - spacing)
    }

    this.yOffset += point_element.node().getBBox().height

    return point_element
  }

  addReferences(){}

}
