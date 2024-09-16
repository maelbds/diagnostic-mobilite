import * as d3 from "d3";

import {strokeWidth} from '../../a-Graphic/Layout'
import {c_yellow} from '../../a-Graphic/Colors'

import {formatFigure} from '../../f-Utilities/util_func';
import {wrap} from '../utilities';

import {Legend, spacing, circle_range_max} from './Legend';


export class PathLegend extends Legend{
  constructor(options){
    super(options)
    this.options = options
  }

  addTitle(){}

  addUnit(){}

  addSpecific(){
    let height_color = 10
    let offset_color = 15

    let {pattern, title} = this.options

    let path_element = this.legend_element.append("g").attr("transform", `translate(0, ${this.yOffset + 5})`)

    let path_d = `M 0,${height_color*2/3} L${circle_range_max*2/3},0 L${circle_range_max*4/3},${height_color} L ${circle_range_max*2},${height_color*1/3}`

    path_element.append("g")
            .selectAll('path')
            .data(pattern.colors)
            .join((enter) => {
              let g = enter.append('g')

              if (pattern.whiteOutline){
                g.append('path')
                .attr('d', path_d)
                .attr('stroke', "white")
                .attr("stroke-width", pattern.strokeWidth + 2)
              }
              g.append('path')
              .attr('d', path_d)
              .attr('stroke', (d, i) => pattern.colors[i%pattern.colors.length])
              .attr("stroke-width", pattern.strokeWidth)
              .attr("stroke-dasharray", pattern.strokeDasharray)

              g.attr("transform", (d, i) => `translate(0, ${i * offset_color})`)
              return g
            })
            .attr('fill', "none")
            .attr("stroke-linecap", "round")
            .attr("stroke-linejoin", "round")

      let title_element = path_element.append('text')
            .attr('x', circle_range_max * 2 + spacing)
            .attr('shape-rendering', 'crispEdges')
            .style('text-anchor', 'start')
            .style('fill', "black")
            .attr('font-family', "source sans pro").attr('font-weight', "400").attr('font-size', "17px")
            .text(title)
      title_element.call(wrap, this.width - (circle_range_max * 2 + spacing))
      title_element.attr("y", (offset_color * pattern.colors.length - (offset_color - height_color))/2 - title_element.node().getBBox().height/2 + 14)

      this.yOffset += path_element.node().getBBox().height + 5

      return path_element
  }

  addReferences(){}

}
