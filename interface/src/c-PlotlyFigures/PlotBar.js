import React, { Component } from 'react';

import {layout_bar} from './plotly_layout';

const Plotly = window.Plotly;

class PlotBar extends React.Component {
  componentDidMount() {
    var data;

    function createStack(name, values, labels, texts, hovertexts){
      return {
        name: name,
        x: labels,
        y: values,
        text: texts,
        hovertext: hovertexts,
        hoverinfo: "text",
        textposition: "inside",
        type: 'bar',
        textfont: {
          color: "#000",
        },
      }
    }
    data = Object.keys(this.props.values).map((key, i) => createStack(key, this.props.values[key], this.props.labels, this.props.texts[key], this.props.hovertexts[key]));

    if (this.props.height !== undefined){
      layout_bar.height = this.props.height;
    }

    if (this.props.colors !== undefined){
      data.map((d, i)=> d.marker = {color: this.props.colors[i]})
    }
    if (this.props.order !== undefined){
      layout_bar.xaxis = {
        categoryorder: "array",
        categoryarray: this.props.order
      }
    }

    Plotly.react(this.props.id, data, layout_bar, {displayModeBar: false});
  }

  componentDidUpdate(){
    var data;

    function createStack(name, values, labels, texts, hovertexts){
      return {
        name: name,
        x: labels,
        y: values,
        text: texts,
        hovertext: hovertexts,
        hoverinfo: "text",
        textposition: "inside",
        type: 'bar',
        textfont: {
          color: "#000",
        },
      }
    }
    data = Object.keys(this.props.values).map((key, i) => createStack(key, this.props.values[key], this.props.labels, this.props.texts[key], this.props.hovertexts[key]));

    if (this.props.height !== undefined){
      layout_bar.height = this.props.height;
    }

    if (this.props.colors !== undefined){
      data.map((d, i)=> d.marker = {color: this.props.colors[i]})
    }

    if (this.props.order !== undefined){
      layout_bar.xaxis = {
        categoryorder:'array',
        categoryarray: this.props.order,
      }
    }

    Plotly.react(this.props.id, data, layout_bar, {displayModeBar: false});
  }


  render() {
    return(
      <div id={this.props.id}></div>
    )
  }
}

export default PlotBar;
