import * as d3 from "d3";


export function verticalStackedBarChart(params){
  let {id, data, getColor, getPropLabel, getLegendLabel, getHoverLabel, getOrder, is_legend_left} = params

  let ratio = 1.4
  let width = 1000
  let height = width * ratio
  let padding = 10

  let text_size_label = 50
  let text_size_prop = 65

  let text_height = 40
  let text_padding = 5
  let text_spacing = 30

  // columns width
  let c1 = width * 3/10
  let c2 = width * 1/10
  let c3 = width * 6/10

  let scale = d3.scaleLinear()
                .domain([0, Object.values(data).reduce((a, b) => a+b, 0)])
                .range([0, height])

  let keys = Object.keys(data).sort(getOrder)

  let svg = d3.select(`#${id}`).html(null).append("svg")
    .attr("viewBox", [0, 0, width, height])
    .attr("class", "verticalStackedBarChart")
    .attr("width", width + 2 * padding)
    .attr("height", height + 2 * padding)
    .attr("style", "width: 100%; height: auto;");

  let h_rect = (d, i) => scale(data[d])
  let y_rect = (d, i) => keys.slice(0, i).map((k, j) => h_rect(k, j)).reduce((a, b) => a+b, 0)

  let wrap = (text_element, content, width) => {
    var words = content.split(/\s+/).reverse(),
        word,
        line = [],
        lineNumber = 0,
        lineHeight = text_height, // ems
        tspan = text_element.append("tspan")
        .attr('font-weight', "300").attr('font-size', text_size_label);
    while (word = words.pop()) {
      line.push(word);
      tspan.text(line.join(" "));
      if (text_element.node().getBBox().width > width) {
          line.pop();
          tspan.text(line.join(" "));
          line = [word];
          tspan = text_element.append("tspan")
                              .attr('shape-rendering', 'crispEdges')
                              .style('fill', "black")
                              .attr('font-weight', "300").attr('font-size', text_size_label)
                              .attr("x", text_element.attr("x"))
                              .attr("dx",  text_element.attr("dx"))
                              .attr("dy", lineHeight*1.5)
                              .text(word);

          // to center vertically
          let text_h = text_element.node().getBBox().height
          text_element.attr("dy", text_height * 1.5 - text_h/2)
        }
      }
  }

  let is_legend_in = (d, i) => {
    let test_text = svg.append('text')
                      .attr('x', 0).attr('y', 100 * i)
                      .attr('shape-rendering', 'crispEdges')
                      .style('fill', "black")
                      .attr('font-family', "source sans pro").attr('font-weight', "400").attr('font-size', "17px")

    let prop_label = test_text.append('tspan')
                              .attr('shape-rendering', 'crispEdges')
                              .style('fill', "black")
                              .attr('font-family', "source sans pro").attr('font-weight', "400").attr('font-size', text_size_prop)
                              .text(`${getPropLabel(d)}% `)

    // to wrap legend label to fit with c3 width
    wrap(test_text, getLegendLabel(d), c3)

    let text_h = test_text.node().getBBox().height
    test_text.remove()

    return (text_h - 2*text_padding) < h_rect(d, i)
  }

  let y_legend_max = 0

  function build_legend(d, i){
    let text = svg.append("g").append("text")
    let legend_in = is_legend_in(d, i)
    let col_w = legend_in ? c3 : c1

    let x = is_legend_left ? (legend_in ? c1 + c2 + c3/2 : c1) : (legend_in ? c3/2 : c3 + c2)
    let dx = is_legend_left ? (legend_in ? 0 : -text_padding) : (legend_in ? 0 : text_padding)
    let text_anchor = is_legend_left ? (legend_in ? "middle" : 'end') : (legend_in ? "middle" : 'start')

    text.attr("x", x)
        .attr("y", y_legend(d, i))
        .attr("dx", dx)
        .attr("dy", text_height/2)
        .attr('shape-rendering', 'crispEdges')
        .style('text-anchor', text_anchor)
        .style('fill', "black")
        .attr('font-family', "source sans pro")
    text.append('tspan')
        .attr('shape-rendering', 'crispEdges')
        .style('fill', "black")
        .attr('font-family', "source sans pro").attr('font-weight', "400").attr('font-size', text_size_prop)
        .text(`${getPropLabel(d)}% `)

    // wrap legend label to fit with either c1 (if legend outside or c3)
    wrap(text, getLegendLabel(d), col_w)

    let y_path = 0;

    if (!legend_in){
      if (y_legend_max > 0){
        y_path = y_legend_max + text.node().getBBox().height/2 + text_spacing
        text.attr("y", y_path)
      } else {
        y_path = y_legend(d, i)
      }
      y_legend_max = text.node().getBBox().y + text.node().getBBox().height
    }

    let path = is_legend_left ? `M ${c1},${y_path} C ${c1 + c2/2},${y_path} ${c1 + c2/2},${y_rect(d, i) + h_rect(d, i)/2} ${c1 + c2},${y_rect(d, i) + h_rect(d, i)/2} ` :
                             `M ${c3 + c2},${y_path} C ${c3 + c2/2},${y_path} ${c3 + c2/2},${y_rect(d, i) + h_rect(d, i)/2} ${c3},${y_rect(d, i) + h_rect(d, i)/2} `

    svg.append("path")
     .attr("d", path)
     .attr("visibility", legend_in ? "hidden" : "visible")
     .attr('stroke', 'black')
     .attr("stroke-width", 1)
     .attr("stroke-dasharray", "4 4")
     .attr("fill", "none")
     .attr("stroke-linecap", "round")
     .attr("stroke-linejoin", "round")
  }

  let y_legend = (d, i) => {
    let supposed_y = y_rect(d, i) + h_rect(d, i) / 2
    if (is_legend_in(d, i)){
      return supposed_y
    } else {
      let legend_items_is_in = keys.slice(0, i).map((k, j) => is_legend_in(k, j))
      let legend_items_y = keys.slice(0, i).map((k, j) => y_legend(k, j))
      let legend_items_out_y = legend_items_y.map((k, j) => legend_items_is_in[j] ? 0 : k).filter((k) => k > 0)
      if (legend_items_out_y.length === 0){
        return Math.max(supposed_y > height/2 ? height/2 : supposed_y, (text_height + text_padding)/2)
      } else {
        return legend_items_out_y[legend_items_out_y.length - 1] + text_spacing
      }
    }
  }

  let x_rect = is_legend_left ? (c1 + c2) : 0
  svg.selectAll()
    .data(keys)
    .join((enter) => {
      let g = enter.append('g')
      .attr("fill", "none")

      g.append('rect')
      .attr("x", (d, i) => x_rect)
      .attr("y", (d, i) => y_rect(d, i))
      .attr("fill", (d, i) => getColor(d))
      .attr("width", c3)
      .attr("rx", 10).attr("ry", 10)
      .attr("height", (d, i) => h_rect(d, i) - 3)
      .append("title")
      .text((d, i) => getHoverLabel(d))
    })

    keys.map((d, i) => build_legend(d, i))
}






export function mirrorVerticalStackedBarChart(params){
  let {id,
    data1, data2,
    getColor,
    getPropLabel1, getPropLabel2,
    getLegendLabel1, getLegendLabel2,
    getHoverLabel1, getHoverLabel2,
    legend1, legend2,
    getOrder} = params

  let ratio = 3/4
  let width = 1000 * 2
  let height = width * ratio
  let padding = 10

  let text_size_label = 50
  let text_size_prop = 60
  let text_size_legend = 55

  let text_height = 35
  let text_padding = 5
  let text_spacing = 30

  // columns width : c1 | c2 | c3 | c_middle | c3 | c2 | c1
  let c1 = width * 3/21
  let c2 = width * 1/21
  let c3 = width * 6/21
  let c_middle = width * 1/21

  // rows height
  let height_chart = height * 9/10
  let height_legend = height * 1/10

  let scale1 = d3.scaleLinear()
                .domain([0, Object.values(data1).reduce((a, b) => a+b, 0)])
                .range([0, height_chart])
  let scale2 = d3.scaleLinear()
                .domain([0, Object.values(data2).reduce((a, b) => a+b, 0)])
                .range([0, height_chart])

  let keys1 = Object.keys(data1).sort(getOrder)
  let keys2 = Object.keys(data2).sort(getOrder)

  let svg = d3.select(`#${id}`).html(null).append("svg")
    .attr("viewBox", [0, 0, width, height])
    .attr("class", "verticalStackedBarChart")
    .attr("width", width + 2 * padding)
    .attr("height", height + 2 * padding)
    .attr("style", "width: 100%; height: auto;");

  let h_rect1 = (d, i) => scale1(data1[d])
  let h_rect2 = (d, i) => scale2(data2[d])
  let y_rect1 = (d, i) => keys1.slice(0, i).map((k, j) => h_rect1(k, j)).reduce((a, b) => a+b, 0)
  let y_rect2 = (d, i) => keys2.slice(0, i).map((k, j) => h_rect2(k, j)).reduce((a, b) => a+b, 0)

  let wrap = (text_element, content, width, text_size) => {
    var words = content.split(/\s+/).reverse(),
        word,
        line = [],
        lineNumber = 0,
        lineHeight = text_height, // ems
        tspan = text_element.append("tspan")
        .attr('font-weight', "300").attr('font-size', text_size);
    while (word = words.pop()) {
      line.push(word);
      tspan.text(line.join(" "));
      if (text_element.node().getBBox().width > width) {
          line.pop();
          tspan.text(line.join(" "));
          line = [word];
          tspan = text_element.append("tspan")
                              .attr('shape-rendering', 'crispEdges')
                              .style('fill', "black")
                              .attr('font-weight', "300").attr('font-size', text_size)
                              .attr("x", text_element.attr("x"))
                              .attr("dx",  text_element.attr("dx"))
                              .attr("dy", lineHeight*1.5)
                              .text(word);

          // to center vertically
          let text_h = text_element.node().getBBox().height
          text_element.attr("dy", text_height * 1.5 - text_h/2)
        }
      }
  }

  let is_legend_in = (d, i, is_legend_left) => {
    let test_text = svg.append('text')
                      .attr('x', 0).attr('y', 100 * i)
                      .attr('shape-rendering', 'crispEdges')
                      .style('fill', "black")
                      .attr('font-family', "source sans pro").attr('font-weight', "400").attr('font-size', "17px")

    let prop_label = test_text.append('tspan')
                              .attr('shape-rendering', 'crispEdges')
                              .style('fill', "black")
                              .attr('font-family', "source sans pro").attr('font-weight', "400").attr('font-size', text_size_prop)
                              .text(is_legend_left ? `${getPropLabel1(d)}% ` : `${getPropLabel2(d)}% `)

    // to wrap legend label to fit with c3 width
    if (is_legend_left){
      wrap(test_text, getLegendLabel1(d), c3, text_size_label)
    } else {
      wrap(test_text, getLegendLabel2(d), c3, text_size_label)
    }

    let text_h = test_text.node().getBBox().height
    test_text.remove()

    let h_rect = is_legend_left ? h_rect1(d, i) : h_rect2(d, i)

    return (text_h - 2*text_padding) < h_rect
  }

  let y_legend_max1 = 0
  let y_legend_max2 = 0

  function build_legend(d, i, is_legend_left){
    let text = svg.append("g").append("text")
    let legend_in = is_legend_in(d, i, is_legend_left)
    let col_w = legend_in ? c3 : c1

    let x = is_legend_left ? (legend_in ? c1 + c2 + c3/2 : c1) : (legend_in ? c1 + c2 + c3 + c_middle + c3/2 : c1 + c2 + c3 + c_middle + c3 + c2)
    let dx = is_legend_left ? (legend_in ? 0 : -text_padding) : (legend_in ? 0 : text_padding)
    let text_anchor = is_legend_left ? (legend_in ? "middle" : 'end') : (legend_in ? "middle" : 'start')

    text.attr("x", x)
        .attr("y", y_legend(d, i, is_legend_left))
        .attr("dx", dx)
        .attr("dy", text_height/2)
        .attr('shape-rendering', 'crispEdges')
        .style('text-anchor', text_anchor)
        .style('fill', "black")
        .attr('font-family', "source sans pro")
    text.append('tspan')
        .attr('shape-rendering', 'crispEdges')
        .style('fill', "black")
        .attr('font-family', "source sans pro").attr('font-weight', "400").attr('font-size', text_size_prop)
        .text(is_legend_left ? `${getPropLabel1(d)}% ` : `${getPropLabel2(d)}% `)

    // wrap legend label to fit with either c1 (if legend outside or c3)
    wrap(text, is_legend_left ? getLegendLabel1(d) : getLegendLabel2(d), col_w, text_size_label)

    let y_path = 0;

    let y_legend_max = is_legend_left ? y_legend_max1 : y_legend_max2

    if (!legend_in){
      if (y_legend_max > 0){
        y_path = y_legend_max + text.node().getBBox().height/2 + text_spacing
        text.attr("y", y_path)
      } else {
        y_path = y_legend(d, i, is_legend_left)
      }
      if (is_legend_left){
        y_legend_max1 = text.node().getBBox().y + text.node().getBBox().height
      } else {
        y_legend_max2 = text.node().getBBox().y + text.node().getBBox().height
      }
    }

    let path = is_legend_left ? `M ${c1},${y_path} C ${c1 + c2/2},${y_path} ${c1 + c2/2},${y_rect1(d, i) + h_rect1(d, i)/2} ${c1 + c2},${y_rect1(d, i) + h_rect1(d, i)/2} ` :
                             `M ${c1 + c2 + c3 + c_middle + c3 + c2},${y_path} C ${c1 + c2 + c3 + c_middle + c3 + c2/2},${y_path} ${c1 + c2 + c3 + c_middle + c3 + c2/2},${y_rect2(d, i) + h_rect2(d, i)/2} ${c1 + c2 + c3 + c_middle + c3},${y_rect2(d, i) + h_rect2(d, i)/2} `

    svg.append("path")
     .attr("d", path)
     .attr("visibility", legend_in ? "hidden" : "visible")
     .attr('stroke', 'black')
     .attr("stroke-width", 1)
     .attr("stroke-dasharray", "4 4")
     .attr("fill", "none")
     .attr("stroke-linecap", "round")
     .attr("stroke-linejoin", "round")
  }

  let y_legend = (d, i, is_legend_left) => {
    let keys = is_legend_left ? keys1 : keys2
    let supposed_y = is_legend_left ? y_rect1(d, i) + h_rect1(d, i) / 2 : y_rect2(d, i) + h_rect2(d, i) / 2
    if (is_legend_in(d, i, is_legend_left)){
      return supposed_y
    } else {
      let legend_items_is_in = keys.slice(0, i).map((k, j) => is_legend_in(k, j, is_legend_left))
      let legend_items_y = keys.slice(0, i).map((k, j) => y_legend(k, j))
      let legend_items_out_y = legend_items_y.map((k, j) => legend_items_is_in[j] ? 0 : k).filter((k) => k > 0)
      if (legend_items_out_y.length === 0){
        return Math.max(supposed_y > height_chart/2 ? height_chart/2 : supposed_y, (text_height + text_padding)/2)
      } else {
        return legend_items_out_y[legend_items_out_y.length - 1] + text_spacing
      }
    }
  }

  svg.selectAll()
    .data(keys1)
    .join((enter) => {
      let g = enter.append('g')
      .attr("fill", "none")

      g.append('rect')
      .attr("x", (d, i) => c1 + c2)
      .attr("y", (d, i) => y_rect1(d, i))
      .attr("fill", (d, i) => getColor(d))
      .attr("width", c3)
      .attr("rx", 10).attr("ry", 10)
      .attr("height", (d, i) => h_rect1(d, i) - 3)
      .append("title")
      .text((d, i) => getHoverLabel1(d))
    })

    svg.selectAll()
      .data(keys2)
      .join((enter) => {
        let g = enter.append('g')
        .attr("fill", "none")

        g.append('rect')
        .attr("x", (d, i) => c1 + c2 + c3 + c_middle)
        .attr("y", (d, i) => y_rect2(d, i))
        .attr("fill", (d, i) => getColor(d))
        .attr("width", c3)
        .attr("rx", 10).attr("ry", 10)
        .attr("height", (d, i) => h_rect2(d, i) - 3)
        .append("title")
        .text((d, i) => getHoverLabel2(d))
      })

    keys1.map((d, i) => build_legend(d, i, true))
    keys2.map((d, i) => build_legend(d, i, false))

    let title1 = svg.append("text")
        .attr("x", c1 + c2 + c3/2)
        .attr("y", height_chart + height_legend/2)
        .attr('shape-rendering', 'crispEdges')
        .style('text-anchor', "middle")
        .style('fill', "black")
        .attr('font-family', "source sans pro").attr('font-weight', "300").attr('font-size', text_size_legend)
    wrap(title1, legend1, c2 + c3, text_size_legend)

    let title2 = svg.append("text")
        .attr("x", c1 + c2 + c3 + c_middle + c3/2)
        .attr("y", height_chart + height_legend/2)
        .attr('shape-rendering', 'crispEdges')
        .style('text-anchor', "middle")
        .style('fill', "black")
        .attr('font-family', "source sans pro").attr('font-weight', "300").attr('font-size', text_size_legend)
    wrap(title2, legend2, c2 + c3, text_size_legend)
}
