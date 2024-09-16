import React, { Component } from 'react';
import * as d3 from "d3";

import LoadingChart from '../f-Utilities/LoadingChart';
import SourcesRow from '../f-Utilities/SourcesRow';
import DownloadButtonLight from '../f-Utilities/DownloadButtonLight';

import {api_call} from '../0-Home/api';
import {formatFigure, downloadCSV, downloadSVGImage} from '../f-Utilities/util_func';
import {c_modes, c_reasons, c_light, c_yellow} from '../a-Graphic/Colors';
import {mirrorVerticalStackedBarChart} from '../j-Charts/verticalStackedBarChart';
import {horizontalBarChart} from '../j-Charts/horizontalBarChart';
import {downloadMapImage} from '../i-Map/utilities';
import {data_loading_nb, data_loading_dist, data_loading_dist_class, data_loading_dist_class_dict, modes_orders} from './data_loading';
import {NbDistFilter} from '../h-Filters/NbDistFilter';
import {data_source_types} from '../f-Utilities/data_source';


class MobilityHome extends React.Component {
  constructor(props){
    super(props)
    let nb_dist_filter = this.filter = NbDistFilter;

    this.init_data = {
      "modes": {
        "number": data_loading_nb,
        "distance": data_loading_dist,
      },
      "dist_class": {
        "dict": data_loading_dist_class_dict,
        "number": data_loading_dist_class,
        "distance": data_loading_dist_class,
        "id": data_loading_dist_class,
      },
      "total_nb": "--",
      "total_dist": "--",
      "total_dist_pers": "--",
      "sources": []
    }

    this.state = {
      id: "modes_home_chart",
      id2: "dist_class_home_chart",
      name_file: "parts_modales_domicile_autre_motif_que_travail",
      name_file2: "classes_distance_domicile_autre_motif_que_travail",
      status: "loading",
      data: this.init_data,
      selected_filter: nb_dist_filter.init
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

  createChart2 = () => {
    let filter_value = this.state.selected_filter
    let class_dist = this.state.data.dist_class[filter_value]
    let class_dist_dict = this.state.data.dist_class.dict
    let filter_labels = this.filter.labels;
    let filter_legend = this.filter.legend;

    let getProp = (d) => class_dist[d]/Object.values(class_dist).reduce((a, b) => a + b, 0) * 100
    let getPropLabel = (d) => this.state.status === "loading" ? "--" : Math.round(getProp(d))

    let getLegendLabel = (d) => d

    let getHoverLabel = (d) => `${Math.round(getProp(d) * 10)/10}% des déplacements (en ${filter_labels[filter_value]}) ${getLegendLabel(d)} soit ${formatFigure(class_dist[d])} ${filter_legend[filter_value]}/jour`

    let getOrder = (a, b) => class_dist_dict[a] - class_dist_dict[b]
    let getColor = (d) => this.state.status === "loading" ? c_light : c_yellow

    horizontalBarChart({
      id: this.state.id2,
      data: class_dist,
      legend: `Répartition par classes de distance des déplacements (en ${filter_labels[filter_value]})`,
      getColor: getColor,
      getPropLabel: getPropLabel,
      getLegendLabel: getLegendLabel,
      getHoverLabel: getHoverLabel,
      getOrder: getOrder,
    })
    this.setState({update: Math.random()})
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

  createTable2 = () => {
    let headlines = ["classe de distance", "part en nombre (%)", "déplacements", "part en distance (%)", "passagers.km"]

    let dist_class = this.state.data.dist_class
    let class_dist_dict = this.state.data.dist_class.dict
    let keys = Object.keys(dist_class.number).sort((a, b) => class_dist_dict[a] - class_dist_dict[b])

    let total_nb = Object.values(dist_class.number).reduce((a, b) => a+b, 0)
    let total_dist = Object.values(dist_class.distance).reduce((a, b) => a+b, 0)

    let rows = keys.map((k) => [
      k,
      Math.round(dist_class.number[k]/total_nb * 1000)/10,
      dist_class.number[k],
      Math.round(dist_class.distance[k]/total_dist * 1000)/10,
      dist_class.distance[k],
    ])

    let format_csv = [(f)=>f, (f)=>formatFigure(f), (f)=>f, (f)=>formatFigure(f), (f)=>f]

    this.setState({
      headlines2: headlines,
      rows2: rows,
      format_csv2: format_csv,
    })
  }

  updateFilter = (filter, k) => {
    this.setState({
      selected_filter: k
    })
  }

  componentDidMount(){
    let endpoints = ["mobility/focus_home_not_work"]
    api_call.call(this, endpoints)

    this.createChart()
    this.createChart2()

    this.createTable()
    this.createTable2()
  }

  componentDidUpdate(prevProps, prevState){
    if(prevState.data !== this.state.data){
      if (this.state.data.modes === null){
        this.setState(this.init_data)
      } else {
        this.createChart()
        this.createChart2()

        this.createTable()
        this.createTable2()
      }
    }
    if (prevState.selected_filter !== this.state.selected_filter){
      this.createChart2()
    }
  }


  render() {
    let {total_nb, total_dist, total_dist_pers} = this.state.data;
    let origin = this.state.data.sources.length > 0 ? (this.state.data.sources.map((s) => s.label).includes("Enquête Mobilité des personnes (SDES 2019)") ? "model" : "emd") : null

    let updateFilter = this.updateFilter
    let selected_filter = this.state.selected_filter
    let filter = this.filter

    return(

          <div className="row">
            <div className="col-12">

              <div className="row align-items-end">

                <div className="col-6">
                  <div className="row">
                    <div className="col-12">
                      <p className="mb-3">Dans cette section, on s'intéresse spécifiquement aux déplacements ayant comme motif <span className="pl-1 pr-1" style={{backgroundColor: c_reasons["domicile ↔ études"]}}>
                      domicile ↔ études</span>, <span className="pl-1 pr-1" style={{backgroundColor: c_reasons["domicile ↔ achats"]}}>
                      domicile ↔ achats</span>, <span className="pl-1 pr-1" style={{backgroundColor: c_reasons["domicile ↔ accompagnement"]}}>
                      domicile ↔ accompagnement</span>, <span className="pl-1 pr-1" style={{backgroundColor: c_reasons["domicile ↔ loisirs"]}}>
                      domicile ↔ loisirs</span>, <span className="pl-1 pr-1" style={{backgroundColor: c_reasons["domicile ↔ visites"]}}>
                      domicile ↔ visites</span>, ou <span className="pl-1 pr-1" style={{backgroundColor: c_reasons["domicile ↔ affaires personnelles"]}}>
                      domicile ↔ affaires personnelles</span>. C'est
                      à dire, les déplacements directement en lien avec le domicile, avec un motif autre que travail.</p>
                      <p className="mb-3">Ils représentent <span className="key_figure">{total_nb === "--" ? "--" : formatFigure(parseFloat(parseFloat(total_nb).toPrecision(3)))}</span> déplacements/jour
                      ayant comme motif le domicile au départ ou à l'arrivée.
                      Cela équivaut à {total_dist === "--" ? "--" : formatFigure(parseFloat(parseFloat(total_dist).toPrecision(3)))} km soit {formatFigure(total_dist_pers)} km/jour en moyenne par personne qui se déplace.</p>
                      <p>Voici comment ces déplacements se décomposent :</p>
                    </div>
                  </div>

                  <div className="row mt-5">
                    <div className="col-12">
                      <h4>classes de distance
                        {origin !== null && <span className={"ml-1 material-symbols-outlined " + origin} title={data_source_types[origin]}>verified</span>}
                      </h4>
                    </div>
                  </div>

                  <div className="row mb-2">
                    <div className="col">
                      {filter.title !== null && <p className="mr-2" style={{display: "inline-block"}}>{filter.title[0].toUpperCase() + filter.title.slice(1)}</p>}

                      <div className="btn-group flex-wrap select_filter_btn mb-1" role="group">
                        {Object.keys(filter.labels).map(k=>
                            <button type="button"
                               key={k}
                               onClick={updateFilter.bind(this, filter, k)}
                               className={selected_filter === k ? "btn active p-0 pl-2 pr-2" : "btn p-0 pl-2 pr-2"}>
                                  <p>{filter.labels[k]}</p>
                            </button>
                          )}
                      </div>

                    </div>
                  </div>

                  <div className="row">
                    <div className="col-12">
                      <div className="row">
                        <div className="col-12">
                          <div id={this.state.id2}></div>
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

                    <DownloadButtonLight onClick={downloadSVGImage.bind(this, d3.select(`#${this.state.id2} svg`).node(), this.state.name_file2)}
                                         title="Télécharger le graphique au format PNG (image)"
                                         label="graphique / .png"/>
                    <DownloadButtonLight onClick={downloadCSV.bind(this, this.state.headlines2, this.state.rows2, this.state.format_csv2, this.state.name_file2)}
                                         title="Télécharger les données au format CSV (tableau)"
                                         label="tableau / .csv"/>
                                         </div>
                     </div>
                  </div>}


                  <SourcesRow selected_sources={this.state.data.sources}/>

                </div>


                <div className="col-6">

                  <div className="row">
                    <div className="col-12">
                      <h4 className="mb-4">modes
                        {origin !== null && <span className={"ml-1 material-symbols-outlined " + origin} title={data_source_types[origin]}>verified</span>}
                      </h4>
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

            </div>
          </div>


    )
  }
}

export default MobilityHome;
