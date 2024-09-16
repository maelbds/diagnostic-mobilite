import * as d3 from "d3";


  // --------------------- to display long text with svg - used in Legend
  // from https://gist.github.com/mbostock/7555321
  export function wrap(text, width, text_height) {
    text.each(function() {
      var text = d3.select(this),
          words = text.text().split(/\s+/).reverse(),
          word,
          line = [],
          lineNumber = 0,
          lineHeight = text_height, // ems
          x = text.attr("x"),
          y = text.attr("y"),
          dy = text.attr("dy") === null ? 0 : parseFloat(text.attr("dy")),
          tspan = text.text(null).append("tspan")
          //.attr('alignment-baseline', 'hanging')
          .attr("x", x).attr("y", y).attr("dy", dy);
      while (word = words.pop()) {
        line.push(word);
        tspan.text(line.join(" "));
        if (tspan.node().getBBox().width > width) {
          line.pop();
          tspan.text(line.join(" "));
          line = [word];
          tspan = text.append("tspan")
          //.attr('alignment-baseline', 'hanging')
          .attr("x", x).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy ).text(word);
        }
      }
    });
  }
