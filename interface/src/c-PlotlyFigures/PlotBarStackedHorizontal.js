import React, { Component } from 'react';

import {layout_bar_stacked} from './plotly_layout';

const Plotly = window.Plotly;

class PlotBarStackedHorizontal extends React.Component {
  componentDidMount() {
    var data;

    function createStack(value, label){
      return {
        x: [value],
        y: ['1'],
        text: label,
        hoverinfo:"text",
        width: 1,
        textposition: "inside",
        orientation: "h",
        type: 'bar',
        textfont: {
          color: "#000",
        },
      }
    }
    data = this.props.values.map((v, i) => createStack(v, this.props.labels[i]));

    if (this.props.height !== undefined){
      layout_bar_stacked.height = this.props.height;
    }

    if (this.props.colors !== undefined){
      data.map((d, i)=> d.marker = {color: this.props.colors[i]})
    }

    Plotly.react(this.props.id, data, layout_bar_stacked, {displayModeBar: false});
  }

  componentDidUpdate(){
    var data;

    function createStack(value, label){
      return {
        x: [value],
        y: ['1'],
        text: label,
        hoverinfo:"text",
        width: 1,
        textposition: "inside",
        orientation: "h",
        type: 'bar',
        textfont: {
          color: "#000",
        },
      }
    }
    data = this.props.values.map((v, i) => createStack(v, this.props.labels[i]));

    if (this.props.height !== undefined){
      layout_bar_stacked.height = this.props.height;
    }

    if (this.props.colors !== undefined){
      data.map((d, i)=> d.marker = {color: this.props.colors[i]})
    }

    Plotly.react(this.props.id, data, layout_bar_stacked, {displayModeBar: false});
  }

  render() {
    return(
      <div id={this.props.id}></div>
    )
  }
}

export default PlotBarStackedHorizontal;
