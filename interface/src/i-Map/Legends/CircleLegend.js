import * as d3 from "d3";

import {strokeWidth} from '../../a-Graphic/Layout'
import {c_yellow, c_violet, c_missing_data} from '../../a-Graphic/Colors'

import {Legend, spacing, circle_range_max} from './Legend';


export class CircleLegend extends Legend{
  constructor(options){
    super(options)
    this.options = options
    this.sqrtScale = d3.scaleSqrt()
           .domain([0, d3.max(options.domain.map((d) => Math.abs(d)))])
           .range(options.range)
  }

  addUnit(){}

  addSpecific(){
    let {domain, unit, format} = this.options
    let circles_domain = [domain[1]/5, domain[1]]

    let hasNegativeValues = domain[0] < 0

    // circles elements
    let circles_element = this.legend_element.append("g").attr("transform", `translate(0, ${this.yOffset + 10})`)

    circles_element.append("g")
            .selectAll('circle')
            .data(circles_domain.reverse())
            .enter().append('circle')
            .attr('r', d => Math.abs(this.sqrtScale(d)))
            .attr('cx', circle_range_max)
            .attr('cy', d => circle_range_max * 2 - Math.abs(this.sqrtScale(d)))
            .style('fill', hasNegativeValues ? c_missing_data : c_yellow)
            .style('stroke', "white")
            .style('stroke-width', strokeWidth)

      circles_element.append('g')
             .selectAll('line')
             .data(circles_domain)
             .enter().append('line')
             .attr('x1', d => circle_range_max)
             .attr('x2', d => circle_range_max * 2 + spacing/2)
             .attr('y1', d => circle_range_max * 2 - 2 * Math.abs(this.sqrtScale(d)))
             .attr('y2', d => circle_range_max * 2 - 2 * Math.abs(this.sqrtScale(d)))
             .style('stroke', "black").style('stroke-width', strokeWidth).style('stroke-dasharray', ('0,2,0'))
             .style('opacity', 0.4)

      circles_element.append('g')
            .selectAll('text')
            .data(circles_domain)
            .enter().append('text')
            .attr('x', circle_range_max * 2 + spacing)
            .attr('y', d => circle_range_max * 2 - 2 * Math.abs(this.sqrtScale(d)))
            .attr('shape-rendering', 'crispEdges')
            .style('text-anchor', 'start')
            .attr('alignment-baseline', 'middle')
            .style('fill', "black")
            .attr('font-family', "source sans pro").attr('font-weight', "300").attr('font-size', "15px")
            .text(d => format(d) + " " + unit)

      //  if negative values
      let height_color = 15
      let offset_color = 20

      if(hasNegativeValues){
        circles_element.append("g")
                .selectAll('rect')
                .data([c_yellow, c_violet])
                .enter().append('rect')
                .attr('x', 0)
                .attr('y', (d, i) => circle_range_max * 2 + 5 + i*offset_color)
                .attr("rx", 3).attr("ry", 3)
                .attr('width', circle_range_max * 2)
                .attr('height', height_color)
                .style('fill', (d) => d)
                .style('stroke', "white").style('stroke-width', strokeWidth)

          circles_element.append('g')
                .selectAll('text')
                .data(["positif", "négatif"])
                .enter().append('text')
                .attr('x', circle_range_max * 2 + spacing)
                .attr('y', (d, i) => circle_range_max * 2 + 5 + i*offset_color + height_color/2)
                .attr('shape-rendering', 'crispEdges')
                .style('text-anchor', 'start')
                .attr('alignment-baseline', 'middle')
                .style('fill', "black")
                .attr('font-family', "source sans pro").attr('font-weight', "300").attr('font-size', "15px")
                .text(d => d)
      }

      this.yOffset += circles_element.node().getBBox().height
  }

}
