import React from 'react';
import * as d3 from "d3";

import LoadingChart from '../f-Utilities/LoadingChart';
import SourcesRow from '../f-Utilities/SourcesRow';
import DownloadButtonLight from '../f-Utilities/DownloadButtonLight';

import {api_call} from '../0-Home/api';
import {formatFigure, downloadCSV, downloadSVGImage} from '../f-Utilities/util_func';
import {c_modes, c_light} from '../a-Graphic/Colors';
import {mirrorVerticalStackedBarChart} from '../j-Charts/verticalStackedBarChart';
import {downloadMapImage} from '../i-Map/utilities';
import {data_loading_nb, data_loading_dist, data_loading_dist_class, data_loading_dist_class_dict, modes_orders} from './data_loading';
import {data_source_types} from '../f-Utilities/data_source';


class Modes extends React.Component {
  constructor(props){
    super(props)

    this.init_data = {
      "modes": {
        "number": data_loading_nb,
        "distance": data_loading_dist,
      },
      "sources": []
    }

    this.state = {
      id: "modes_chart",
      name_file: "parts_modales",
      status: "loading",
      data: this.init_data,
    }
  }

  createChart = () => {
    let modes = this.state.data.modes
    let modes_nb = modes.number
    let modes_dist = modes.distance

    let getProp_nb = (d) => modes_nb[d]/Object.values(modes_nb).reduce((a, b) => a + b, 0) * 100
    let getProp_dist = (d) => modes_dist[d]/Object.values(modes_dist).reduce((a, b) => a + b, 0) * 100

    let getPropLabel_nb = (d) => this.state.status === "loading" ? "--" : Math.round(getProp_nb(d))
    let getPropLabel_dist = (d) => this.state.status === "loading" ? "--" : Math.round(getProp_dist(d))

    let getLegendLabel = (d) => d

    let getHoverLabel_nb = (d) => `${Math.round(getProp_nb(d) * 10)/10}% ${getLegendLabel(d)} soit ${formatFigure(modes_nb[d])} déplacements/jour`
    let getHoverLabel_dist = (d) => `${Math.round(getProp_dist(d) * 10)/10}% ${getLegendLabel(d)} soit ${formatFigure(modes_dist[d])} km/jour`

    let getOrder = (a, b) => modes_orders[b] - modes_orders[a]
    let getColor = (d) => this.state.status === "loading" ? c_light : c_modes[d]

    mirrorVerticalStackedBarChart({
      id: this.state.id,
      data1: modes_nb,
      data2: modes_dist,
      legend1: "Répartition modale en nombre de déplacements",
      legend2: "Répartition modale en km parcourus (passagers.km)",
      getColor: getColor,
      getPropLabel1: getPropLabel_nb,
      getPropLabel2: getPropLabel_dist,
      getLegendLabel1: getLegendLabel,
      getLegendLabel2: getLegendLabel,
      getHoverLabel1: getHoverLabel_nb,
      getHoverLabel2: getHoverLabel_dist,
      getOrder: getOrder,
    })
  }

  createTable = () => {
    let headlines = ["mode", "part en nombre (%)", "déplacements", "part en distance (%)", "passagers.km"]

    let modes = this.state.data.modes
    let keys = Object.keys(modes.number)

    let total_nb = Object.values(modes.number).reduce((a, b) => a+b, 0)
    let total_dist = Object.values(modes.distance).reduce((a, b) => a+b, 0)

    let rows = keys.map((k) => [
      k,
      Math.round(modes.number[k]/total_nb * 1000)/10,
      modes.number[k],
      Math.round(modes.distance[k]/total_dist * 1000)/10,
      modes.distance[k],
    ])

    let format_csv = [(f)=>f, (f)=>formatFigure(f), (f)=>f, (f)=>formatFigure(f), (f)=>f]

    this.setState({
      headlines: headlines,
      rows: rows,
      format_csv: format_csv,
    })
  }

  componentDidMount(){
    let endpoints = ["mobility/modes"]
    api_call.call(this, endpoints)

    this.createChart()
    this.createTable()
  }

  componentDidUpdate(prevProps, prevState){
    if(prevState.data !== this.state.data){
      if (this.state.data.modes === null){
        this.setState(this.init_data)
      } else {
        this.createChart()
        this.createTable()
      }
    }
  }

  render(){
    let origin = this.state.data.sources.length > 0 ? (this.state.data.sources.map((s) => s.label).includes("Enquête Mobilité des personnes (SDES 2019)") ? "model" : "emd") : null

    if (this.state.status === "error") {
      return (
        <p>Erreur...</p>
      )
    }
    else{
      return(
        <div className="row">
          <div className="col-12">

            <div className="row">
              <div className="col-12">
                <h3 className="mb-4">modes
                  {origin !== null && <span className={"ml-1 material-symbols-outlined " + origin} title={data_source_types[origin]}>verified</span>}
                </h3>
              </div>
            </div>

            <div className="row">
              <div className="col-12">
                <div className="row">
                  <div className="col-12">
                    <div id={this.state.id}></div>
                  </div>
                </div>

                {this.state.status === "loading" && <LoadingChart />}
              </div>
            </div>

            {this.state.status === "loaded" &&
            <div className="row justify-content-between align-items-start mt-3 mb-2">
              <div className="col-5">
                <p className="sources"><i>Note : les pourcentages sont arrondis ainsi la somme n'est pas toujours égale à 100%.</i></p>
              </div>

              <div className="col-7 mt-1">
              <div className="row justify-content-end">

              <DownloadButtonLight onClick={downloadSVGImage.bind(this, d3.select(`#${this.state.id} svg`).node(), this.state.name_file)}
                                   title="Télécharger le graphique au format PNG (image)"
                                   label="graphique / .png"/>
              <DownloadButtonLight onClick={downloadCSV.bind(this, this.state.headlines, this.state.rows, this.state.format_csv, this.state.name_file)}
                                   title="Télécharger les données au format CSV (tableau)"
                                   label="tableau / .csv"/>
                                   </div>
               </div>
            </div>}

            <SourcesRow selected_sources={this.state.data.sources}/>

          </div>
        </div>
      );
    }
  }
}

export default Modes;
