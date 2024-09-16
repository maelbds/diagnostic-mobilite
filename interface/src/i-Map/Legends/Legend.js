import * as d3 from "d3";

import {strokeWidth} from '../../a-Graphic/Layout'
import {c_yellow} from '../../a-Graphic/Colors'

import {formatFigure} from '../../f-Utilities/util_func';
import {wrap} from '../utilities';


export const spacing = 10
export const circle_range_max = 25


export class Legend{
  constructor(options){
    let default_options = {
      title: null,
      subtitle: null,
      unit: null,
      colors: null,
      thresholds: null,
      references: null,
      format: (d) => d, // function to format figures
    }
    this.options = {...default_options, ...options}
  }


  addTitle(title){
    let title_element = this.legend_element.append("g")
    title_element.append('text')
          .attr('x', 0).attr('y', 0)
          .attr('shape-rendering', 'crispEdges')
          .style('text-anchor', 'start')
          .style('fill', "black")
          .attr('font-family', "source sans pro").attr('font-weight', "400").attr('font-size', "17px")
          .text(title)
          .call(wrap, this.width)

    let offSetText = title_element.select("tspan").node().getBBox().height
    title_element.attr("transform", `translate(0, ${this.yOffset + offSetText - 7})`)

    this.yOffset += title_element.node().getBBox().height

    return title_element
  }

  addSubTitle(subtitle){
    let subtitle_element = this.legend_element.append("g")
    subtitle_element.append('text')
          .attr('x', 0).attr('y', 0)
          .attr('shape-rendering', 'crispEdges')
          .style('text-anchor', 'start')
          .style('fill', "black")
          .attr('font-family', "source sans pro").attr('font-weight', "300").attr('font-size', "15px")
          .text(subtitle)
          .call(wrap, this.width)

    let offSetText = subtitle_element.select("tspan").node().getBBox().height
    subtitle_element.attr("transform", `translate(0, ${this.yOffset + offSetText - 7})`)

    this.yOffset += subtitle_element.node().getBBox().height

    return subtitle_element
  }

  addUnit(unit){
    let unit_element = this.legend_element.append("g")
    unit_element.append('text')
          .attr('x', 0).attr('y', 0)
          .attr('shape-rendering', 'crispEdges')
          .style('text-anchor', 'start')
          .style('fill', "black")
          .attr('font-family', "source sans pro").attr('font-weight', "300").attr('font-size', "15px")
          .text(`(${unit})`)
          .call(wrap, this.width)

    let offSetText = unit_element.select("tspan").node().getBBox().height
    unit_element.attr("transform", `translate(0, ${this.yOffset + offSetText - 5})`)

    this.yOffset += unit_element.node().getBBox().height

    return unit_element
  }

  addReferences(references, unit, withUnit = true){
    let references_element = this.legend_element.append("g").attr("transform", `translate(0, ${this.yOffset + 5})`)
    let references_element_text = references_element.append('text')
                      .attr('x', 0).attr('y', 0)
                      .attr('shape-rendering', 'crispEdges')
                      .style('text-anchor', 'start')
                      .attr('alignment-baseline', 'hanging')
                      .style('fill', "black")
                      .attr('font-family', "source sans pro").attr('font-weight', "300").attr('font-size', "15px")

    references.forEach((r, i) => {
        references_element_text.append('tspan')
                        .attr('alignment-baseline', 'hanging')
                        .attr('text-decoration', 'underline')
                        .attr("x", 0)
                        .attr("y", i * 1.3 + "em")
                        .text(r.label)
        references_element_text.append('tspan')
                        .attr('alignment-baseline', 'hanging')
                        .attr('dx', 5)
                        .attr("y", i * 1.3 + "em")
                        .text(withUnit ? r.value + " " + unit : r.value)
    });

    this.yOffset += references_element.node().getBBox().height + 5

    return references_element
  }

  addSpecific(){}

  addTo(legend){
    this.width = legend.attr("width")
    this.yOffset = 0

    let {title, subtitle, unit, references} = this.options
    this.legend_element = legend.append("g").attr("class", "legend_element")

    title !== null && this.addTitle(title)
    subtitle !== null && this.addSubTitle(subtitle)
    unit !== null && this.addUnit(unit)

    this.addSpecific()

    references !== null && references !== {} && unit !== null && this.addReferences(references, unit)

    return this.legend_element
  }

}
