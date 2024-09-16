import React from 'react';

import Info from '../f-Utilities/Info'
import SourcesRow from '../f-Utilities/SourcesRow';

import {formatFigure} from '../f-Utilities/util_func';

import {api_url} from '../0-Home/api';

import {c_categories, c_missing_data} from '../a-Graphic/Colors';

import * as d3 from "d3";


class IdentityGeneral extends React.Component{
  constructor(props) {
    super(props);

    this.state = {
      population: null,
      households: null,
      jobs_nb: null,
      jobs_concentration: null,
      motorisation_rate: null,
      density: null,

      sources: [],
    }
  }

  componentDidMount(){
    let myHeaders = new Headers()
    myHeaders.append("Accept", "application/json");
    myHeaders.append("Content-Type", "application/json");
    myHeaders.append("Access-Control-Allow-Origin", "*");
    myHeaders.append("Cache-Control", "max-age=604800");

    let geo_codes = this.props.geography.com.map((c) => c.geo_code)

    Promise.all([
      fetch(`${api_url}territory/key_figures?geo_codes=${geo_codes}`, {
            method: "GET",
            headers: myHeaders,
          })]
    ).then(results => Promise.all(results.map(r => r.json()))
    ).then((responses) => {
      this.setState({...responses[0].key_figures, sources: responses[0].sources, references: responses[0].references.france})
    }).catch((err) => {
      this.setState({
        status: "error",
        error: err.toString()
      });
    })

    this.chart_h = 250
    this.chart_w = 700
    this.svg = d3.select("#pop_status_chart").append("svg")
                  //.attr("width", "100%")
                  //.attr("height", this.chart_h + "px")
      .attr("viewBox", [0, 0, this.chart_w, this.chart_h])
      .attr("width", this.chart_w)
      .attr("height", this.chart_h)
                  .attr("style", "width: 100%; height: auto;");
  }

  componentDidUpdate(){
    if (this.state.employed !== null && this.svg.selectChildren().nodes().length === 0){
      let width = this.chart_w // this.svg.node().getBoundingClientRect().width
      let chart_h = this.chart_h
      let ticks_h = 40
      let labels_h = 60

      let all_status = ["employed", "unemployed", "retired", "scholars", "other"]
      let all_status_fr = ["actifs & actives", "au chômage", "à la retraite", "scolaires", "autres"]
      let spacing = 10
      let width_item = width / all_status.length - spacing

      let ratio_ref = 2/3

      let getPercent = (l) => Math.round(this.state[l] / this.state.population * 1000)/10
      let getValue = (l) => this.state[l]
      let getPercentFr = (l) => Math.round(this.state.references[l] / this.state.references.population * 1000)/10

      let allPercent = all_status.map(getPercent).concat(all_status.map(getPercentFr))

      let scale = d3.scaleLinear()
                    .domain([0, Math.max(...allPercent)])
                    .range([0, this.chart_h - labels_h - ticks_h])

      this.svg.selectAll()
        .data(all_status)
        .join((enter) => {
          let g = enter.append('g')
          .attr("fill", "none")

          g.append('rect')
          .attr("x", (d, i) => i * (width_item + spacing))
          .attr("y", (d, i) => chart_h - labels_h - scale(getPercent(d)))
          .attr("fill", (d, i) => c_categories[i])
          .attr("width", width_item*ratio_ref)
          .attr("rx", 3).attr("ry", 3)
          .attr("height", (d, i) => scale(getPercent(d)))

          g.append('rect')
          .attr("x", (d, i) => i * (width_item + spacing) + width_item*ratio_ref)
          .attr("y", (d, i) => chart_h - labels_h - scale(getPercentFr(d)))
          .attr("fill", (d, i) => c_categories[i]+"4d")
          .attr("width", width_item*(1-ratio_ref))
          .attr("rx", 3).attr("ry", 3)
          .attr("height", (d, i) => scale(getPercentFr(d)))

          // x axis
          g.append('text')
          .attr("x", (d, i) => i * (width_item + spacing) + width_item / 2)
          .attr("y", (d, i) => chart_h - 35)
          .attr('shape-rendering', 'crispEdges')
          .style('text-anchor', 'middle')
          .style('fill', "black")
          .attr('font-family', "source sans pro").attr('font-weight', "400").attr('font-size', "17px")
          .text((d, i) => all_status_fr[i])
          g.append('text')
          .attr("x", (d, i) => i * (width_item + spacing) + width_item / 2)
          .attr("y", (d, i) => chart_h - 15)
          .attr('shape-rendering', 'crispEdges')
          .style('text-anchor', 'middle')
          .style('fill', "black")
          .attr('font-family', "source sans pro").attr('font-weight', "300").attr('font-size', "17px")
          .text((d) => formatFigure(getValue(d)))

          // label territory
          g.append('text')
          .attr("x", (d, i) => i * (width_item + spacing) + width_item*ratio_ref/2)
          .attr("y", (d, i) => chart_h - labels_h - scale(getPercent(d)) - 15)
          .attr('shape-rendering', 'crispEdges')
          .style('text-anchor', 'middle')
          .style('fill', "black")
          .attr('font-family', "source sans pro").attr('font-weight', "400").attr('font-size', "22px")
          .text((d) => formatFigure(getPercent(d), 2) + "%")

          // label fr
          g.append('text')
          .attr("x", (d, i) => i * (width_item + spacing) + width_item*ratio_ref + width_item*(1-ratio_ref)/2)
          .attr("y", (d, i) => chart_h - labels_h - scale(getPercentFr(d)) - 20)
          .attr('shape-rendering', 'crispEdges')
          .style('text-anchor', 'middle')
          .style('fill', "black")
          .attr('font-family', "source sans pro").attr('font-weight', "300").attr('font-size', "13px")
          .text((d) => formatFigure(getPercentFr(d), 2) + "%")
          g.append('text')
          .attr("x", (d, i) => i * (width_item + spacing) + width_item*ratio_ref + width_item*(1-ratio_ref)/2)
          .attr("y", (d, i) => chart_h - labels_h - scale(getPercentFr(d)) - 5)
          .attr('shape-rendering', 'crispEdges')
          .style('text-anchor', 'middle')
          .style('fill', "black")
          .attr('font-family', "source sans pro").attr('font-weight', "300").attr('font-size', "12px")
          .text("France")

        })
      }
  }

  render(){
    function formatValue(value){
      if (value === null){
        return "---"
      } else {
        return formatFigure(value)
      }
    }

    let {population, households, jobs_nb, jobs_concentration, motorisation_rate, density,
         sources} = this.state

    const getValue = (n) => this.state[n]
    const getLabel = (n) => `${this.state[n]}</br>${Math.round(this.state[n]/population*100)} %`

    return(

  <div className="row">
    <div className="col">

      <h3 className="">vue d'ensemble</h3>

      <p><span className="key_figure">{formatValue(population)}</span> habitant.es </p>
      <p className="mb-3">pour <b>{formatValue(households)}</b> ménages</p>

      <div id="pop_status_chart"></div>

      <p className="mt-3"><span className="key_figure">{formatValue(jobs_nb)}</span> emplois sur le territoire</p>
      <p>soit un <b>indicateur de concentration d'emploi de {formatValue(jobs_concentration)}
      </b> <Info content="L'indicateur de concentration d'emploi est égal au nombre d'emplois dans la zone pour 100 actifs ayant un emploi résidant dans la zone (définition INSEE)."/>
      </p>

      <p className="mt-2"><span className="key_figure">{formatValue(motorisation_rate)} %</span> des ménages sont motorisés</p>
      <p className="mt-2 mb-2">Une densité de <span className="key_figure">{formatValue(density)}</span> hab/km²</p>

      <SourcesRow selected_sources={sources}/>

   </div>
  </div>

  );
  }
}

export default IdentityGeneral;
