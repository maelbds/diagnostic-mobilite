import * as d3 from "d3";

import {wrap} from './utilities';


export function horizontalBarChart(params){
  let {id, data, legend, getColor, getPropLabel, getLegendLabel, getHoverLabel, getOrder} = params
  let is_legend_left = true;

  let ratio = 1/2
  let width = 2000
  let height = width * ratio
  let padding = 10

  let text_size_label = 50
  let text_size_prop = 60
  let text_size_legend = 55

  let text_height = 60
  let text_padding = 5
  let text_spacing = 30

  let bar_space_ratio = 3/4

  // columns width
  let c1 = width * 3/10
  let c2 = width * 1/10
  let c3 = width * 6/10

  // rows height
  let r1 = text_height
  let r3 = height * 2/10
  let r2 = height - r1 - r3

  let scale = d3.scaleLinear()
                .domain([0, Math.max(...Object.values(data))])
                .range([0, r2])

  let keys = Object.keys(data).sort(getOrder)

  let svg = d3.select(`#${id}`).html(null).append("svg")
    .attr("viewBox", [0, 0, width, height])
    .attr("class", "verticalStackedBarChart")
    .attr("width", width + 2 * padding)
    .attr("height", height + 2 * padding)
    .attr("style", "width: 100%; height: auto;");


  let h_rect = (d, i) => scale(data[d])
  let w_rect = width * bar_space_ratio / keys.length
  let x_rect = (d, i) => i*(bar_width + space_width) + space_width/2

  let bar_width = width * bar_space_ratio / keys.length
  let space_width = width * (1-bar_space_ratio) / keys.length

  svg.selectAll()
    .data(keys)
    .join((enter) => {
      let g = enter.append('g')
      .attr("fill", "none")

      g.append('rect')
      .attr("x", x_rect)
      .attr("y", (d, i) => r2 - h_rect(d, i) + r1)
      .attr("rx", "10").attr("ry", "10")
      .attr("fill", (d, i) => getColor(d))
      .attr("width", w_rect)
      .attr("height", (d, i) => h_rect(d, i))
      .append("title")
      .text((d, i) => getHoverLabel(d))

      // Proportion label
      g.append('text')
        .attr("x", (d, i) => x_rect(d, i) + bar_width/2)
        .attr("y", (d, i) => r2 - h_rect(d, i) + r1)
        .attr("dy", - 20)
        .attr('shape-rendering', 'crispEdges')
        .style('text-anchor', "middle")
        .style('fill', "black")
        .attr('font-family', "source sans pro").attr('font-weight', "400").attr('font-size', text_size_prop)
        .text((d, i) => `${getPropLabel(d)}% `)

      // Legend Label
      g.append('text')
        .attr("x", (d, i) => x_rect(d, i) + bar_width/2)
        .attr("y", (d, i) => r2 + r1)
        .attr("dy", text_height)
        .attr('shape-rendering', 'crispEdges')
        .style('text-anchor', "middle")
        .style('fill', "black")
        .attr('font-family', "source sans pro").attr('font-weight', "300").attr('font-size', text_size_label)
        .text((d, i) => `${getLegendLabel(d)}`)
        .call(wrap, bar_width + space_width, text_height)

    })

    // Chart legend
    svg.append("text")
        .attr("x", width/2)
        .attr("y", r1 + r2 + r3/2)
        .attr("dy", text_height)
        .attr('shape-rendering', 'crispEdges')
        .style('text-anchor', "middle")
        .style('fill', "black")
        .attr('font-family', "source sans pro").attr('font-weight', "300").attr('font-size', text_size_legend)
        .text(legend)
}
