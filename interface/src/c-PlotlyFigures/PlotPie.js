import React, { Component } from 'react';

import {layout_pie} from './plotly_layout';

const Plotly = window.Plotly;

class PlotPie extends React.Component {

    componentDidMount() {
      var text_position = this.props.text
      let data = [{
        values: this.props.values,
        labels: this.props.labels,
        textinfo: "label",
        hovertext: this.props.text,
        hoverinfo: "text",
        textposition: this.props.textposition,
        automargin: true,
        rotation: 270,
        direction: "clockwise",
        sort: false,
        type: 'pie'
      }];

      let layout = Object.assign({}, layout_pie)

      if (this.props.height !== undefined){
        layout.height = this.props.height;
      }

      if (this.props.width !== undefined){
        layout.width = this.props.width;
      }

      if (this.props.colors !== undefined){
        data[0].marker = {colors: this.props.colors};
      }
      Plotly.react(this.props.id, data, layout);
    }


    componentDidUpdate() {
      let data = [{
        values: this.props.values,
        labels: this.props.labels,
        textinfo: "label",
        hovertext: this.props.text,
        hoverinfo: "text",
        textposition: this.props.textposition,
        automargin: true,
        rotation: 270,
        direction: "clockwise",
        sort: false,
        type: 'pie'
      }];

      let layout = Object.assign({}, layout_pie)

      if (this.props.height !== undefined){
        layout.height = this.props.height;
      }

      if (this.props.width !== undefined){
        layout.width = this.props.width;
      }

      if (this.props.colors !== undefined){
        data[0].marker = {colors: this.props.colors};
      }

      Plotly.react(this.props.id, data, layout);
    }

  render() {
    return(
      <div id={this.props.id}></div>
    )
  }
}

PlotPie.defaultProps = {
  textposition: "outside"
}

export default PlotPie;
