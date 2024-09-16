import * as d3 from "d3";

import {strokeWidth} from '../../a-Graphic/Layout'
import {c_yellow} from '../../a-Graphic/Colors'

import {formatFigure} from '../../f-Utilities/util_func';
import {wrap} from '../utilities';

import {Legend, spacing, circle_range_max} from './Legend';


export class GridLegend extends Legend{
  constructor(options){
    super(options)
    this.options = options
  }

  addUnit(){}

  addSpecific(){
    let height_color = 20
    let offset_color = 25

    let {thresholds, colors, unit, format} = this.options

    let grid_element = this.legend_element.append("g").attr("transform", `translate(0, ${this.yOffset + 5})`)

    for (let v=0; v<3; v++){
      grid_element.append("g")
              .selectAll('circle')
              .data(colors)
              .enter().append('circle')
              .attr('cx', circle_range_max/3*(2*v+1)).attr('cy', (d, i) => i*offset_color + circle_range_max/3)
              .attr("r", circle_range_max/3)
              .style('fill', (d) => d)
    }

      grid_element.append('g')
          .selectAll('text')
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

      this.yOffset += grid_element.node().getBBox().height + 5

      return grid_element
  }

  addReferences(){}

}
