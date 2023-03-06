import React, { Component } from 'react';

import getMyMap from '../b-LeafletMap/leaflet_map';
import {createCommunesNamesLayerEasy} from '../b-LeafletMap/LeafletMapElement/createCommuneName';

import {getWorkPlaceElements, getWorkPlaceElementsTable} from './work_places';
import {getWorkFlowsCommuneElements} from './work_flows_commune';
import {getWorkFlowsAllElements, getFlowsTable} from './work_flows_all';
import {getWorkFlowsExtElements} from './work_flows_ext';

import LeafletMapLegend from '../b-LeafletMap/LeafletMapLegend';
import Table from '../d-Table/Table';
import ViewButton from '../f-Utilities/ViewButton';
import DownloadButton from '../f-Utilities/DownloadButton';
import DataSelectionButton from '../f-Utilities/DataSelectionButton';

import {c_missing_data, c_gradient_reds_greens} from '../a-Graphic/Colors';
import {formatFigure, downloadCSV, cols_to_rows} from '../f-Utilities/util_func';

class Work extends React.Component {
  getCommunesMap(selected, params){
    /* COMMUNES */
    let communes = this.props.territory.communes;
    let communes_coords = communes.map((c) => c.center);
    let communes_names = communes.map((c) => c.name);

    if(selected == "work_places"){
      var {layer_to_fit, layers, legend, sources} = getWorkPlaceElements(communes, this.props.territory.areas_by_reason)
    }
    else if(selected == "work_flows_commune"){
      var {layer_to_fit, layers, legend, sources} = getWorkFlowsCommuneElements(communes,
                                                                                this.props.territory.influence_communes,
                                                                                this.props.territory.work_communes,
                                                                                params.flow_commune_index,
                                                                                this.selectCommuneIndex.bind(this))
    }
    else if(selected == "work_flows_all"){
      var {layer_to_fit, layers, legend, sources} = getWorkFlowsAllElements(communes,
                                                                            this.props.territory.influence_communes,
                                                                            this.props.territory.work_communes,
                                                                            params.limit_all_flows,
                                                                            this.selectCommuneAllLimit.bind(this))
    }
    else if(selected == "work_flows_ext"){
      var {layer_to_fit, layers, legend, sources} = getWorkFlowsExtElements(communes,
                                                                            this.props.territory.influence_communes,
                                                                            this.props.territory.work_communes,
                                                                            params.limit_ext_flows,
                                                                            this.selectCommuneExtLimit.bind(this))
    }
    layers.push(createCommunesNamesLayerEasy(communes))

    let sources_map = sources
    return {selected, params, layer_to_fit, layers, legend, sources_map}
  }

  getCommunesTable(selected){
    let communes = this.props.territory.communes;

    if (selected == "work_places"){
      var {headlines, rows, align, format_table, format_csv, sources_table, name_csv} = getWorkPlaceElementsTable(communes, this.props.territory.areas_by_reason)
    }
    else {
      var {headlines, rows, align, format_table, format_csv, sources_table, name_csv} = getFlowsTable(communes, this.props.territory.influence_communes, this.props.territory.work_communes)
    }
    return {headlines, rows, align, format_table, format_csv, sources_table, name_csv}
  }


  constructor(props) {
    super(props);
    let selected_init = "work_places"
    let params = {flow_commune_index: null, limit_all_flows: 50, limit_ext_flows: 50}

    this.state = Object.assign({}, {
      viewMap: true,
      viewTable: false,
    },
    this.getCommunesMap(selected_init, params),
    this.getCommunesTable(selected_init));
  }

  setView = (view) => {
      this.setState({
        viewMap: view=="map",
        viewTable: view=="table",
      })
  }
  displayCategory = (selected) => {
    this.setState(function(prevState, prevProps){
      this.setState(this.getCommunesMap(selected, prevState.params))
    })
    this.setState(this.getCommunesTable(selected))
  }
  selectCommuneIndex = (flow_commune_index) => {
      this.setState(function(prevState, prevProps){
        prevState.params.flow_commune_index = flow_commune_index
        return this.getCommunesMap(prevState.selected, prevState.params)
      })
  }
  selectCommuneAllLimit = (limit_all_flows) => {
      this.setState(function(prevState, prevProps){
        prevState.params.limit_all_flows = limit_all_flows
        return this.getCommunesMap(prevState.selected, prevState.params)
      })
  }
  selectCommuneExtLimit = (limit_ext_flows) => {
      this.setState(function(prevState, prevProps){
        prevState.params.limit_ext_flows = limit_ext_flows
        return this.getCommunesMap(prevState.selected, prevState.params)
      })
  }

  componentDidMount() {
    // --- init map
    let mymap = this.mymap = getMyMap("work_map", true, 0.3);
    // --- add layers
    this.state.layers.map((layer)=>layer.addTo(mymap))
    // --- center the map
    mymap.fitBounds(this.state.layer_to_fit.getBounds());
  }

  componentDidUpdate(prevProps, prevState) {
    // --- update
    prevState.layers.map((layer)=>this.mymap.removeLayer(layer))
    this.state.layers.map((layer)=>layer.addTo(this.mymap))
  }

  render() {
    let data_list = [{selected: "work_places", label: "lieux d'emplois"},
                     {selected: "work_flows_commune", label: "flux domicile → travail", label_i: "(détail par commune)" },
                     {selected: "work_flows_all", label: "flux domicile → travail", label_i: "(vue d'ensemble)"},
                     {selected: "work_flows_ext", label: "flux domicile → travail", label_i: "(depuis territoires extérieurs)"}]

    return(
          <div className="row content mt-4 mb-5">

            <div className="col-3">
                <div className="row">
                  <div className="col-12">
                    <h3 className="mb-3">emploi</h3>
                  </div>
                </div>

                <div className="row">
                  <div className="col-12 line-border">
                    {data_list.map((d)=>
                      <DataSelectionButton selected={this.state.selected === d.selected}
                                           display_category={this.displayCategory.bind(this, d.selected)} label={d.label} label_i={d.label_i} />
                    )}
                  </div>
                </div>

            </div>

            <div className="col-9">
              <div className="row">
                <div className="col-12" style={{display: this.state.viewMap ? "block" : "none"}}>
                  <LeafletMapLegend legend={this.state.legend}
                                    all_sources={this.props.territory.sources}
                                    concerned_sources={this.state.sources_map}
                                    id="work_map"
                                    height="500px"/>
                </div>

                <div className="col-12" style={{display: this.state.viewTable ? "block" : "none"}}>
                 <Table headlines={this.state.headlines}
                        rows={this.state.rows}
                        align={this.state.align}
                        format={this.state.format_table}
                        all_sources={this.props.territory.sources}
                        concerned_sources={this.state.sources_table}
                        height="500px"/>
                </div>
              </div>

              <div className="row mt-3">
                <ViewButton active={this.state.viewMap} label="Carte" setView={this.setView.bind(this, "map")} />
                <ViewButton active={this.state.viewTable} label="Tableau" setView={this.setView.bind(this, "table")} />

                <DownloadButton download={downloadCSV.bind(this, this.state.headlines, this.state.rows, this.state.format_csv, this.state.name_csv)} />
              </div>

          </div>
        </div>
    )
  }
}

export default Work;
