import React, { Component } from 'react';
import * as d3 from "d3";

const Plot = window.Plot

class VerticalBarChart extends React.Component {
  componentDidMount(){
    let svg = Plot.barY([{letter: "A", frequency: 30}], {x: "letter", y: "frequency"}).plot()
    
    d3.select(`#${this.props.id}`).node().appendChild(svg)
  }

  render() {
    return(
      <div id={this.props.id}></div>
    )
  }
}

VerticalBarChart.defaultProps = {
  height: "200px"
}

export default VerticalBarChart;
