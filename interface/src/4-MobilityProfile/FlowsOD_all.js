import React, { Component } from 'react';

import getMyMap from '../b-LeafletMap/leaflet_map';
import {createCommunesNamesLayerEasy} from '../b-LeafletMap/LeafletMapElement/createCommuneName';
import {getLegendMode} from '../b-LeafletMap/leaflet_map';
import {createFlowsLayer} from '../b-LeafletMap/LeafletMapElement/createFlow'
import {createCommuneBordersLayer} from '../b-LeafletMap/LeafletMapElement/createCommune'

import LeafletMapLegend from '../b-LeafletMap/LeafletMapLegend';
import Table from '../d-Table/Table';
import ViewButton from '../f-Utilities/ViewButton';
import DownloadButton from '../f-Utilities/DownloadButton';
import DataSelectionButton from '../f-Utilities/DataSelectionButton';

import {c_light, c_background, c_gradient_reds} from '../a-Graphic/Colors';
import {formatFigure, downloadCSV, cols_to_rows, titleCase} from '../f-Utilities/util_func';


class FlowsOD_all extends React.Component {
  getCommunesMap(unit, unit_label, unit_legend, flows_limit){
    let territory = this.props.territory

    /* COMMUNES */
    let communes = territory.communes;
    let communes_coords = communes.map((c) => c.center);
    let communes_names = communes.map((c) => c.name);

    /* Geocode to Name and Coords DICT */
    let geo_code_dict = territory.geo_code_dict;
    if(geo_code_dict == null){
      geo_code_dict = {}
    }
    let all_communes = communes.concat(territory.influence_communes).concat(territory.work_communes)
    all_communes.map((c)=>geo_code_dict[c.geo_code] = {"center": c.center, "name": c.name})

    /* FLOWS */
    let flows_od = territory.travels_analysis["3_flows"].flows_commune_all[unit];
    flows_od.sort((a,b)=> b[2] - a[2])
    flows_od = flows_od.slice(0, flows_limit)
    let total_flows = territory.travels_analysis["1_key_figures"].total[unit]

    let flows_coords = flows_od.map((f)=> [geo_code_dict[f[0]]["center"], geo_code_dict[f[1]]["center"]])
    let flows_masses = flows_od.map((f)=> f[2])
    let flows_labels = flows_od.map((f)=> geo_code_dict[f[0]]["name"] + " ↔ " + geo_code_dict[f[1]]["name"]  + " : " + formatFigure(f[2], 3) + " " + unit_label + " (" + formatFigure(f[2]/total_flows*100, 2) + "%)")

    let total_flows_masses_displayed = flows_masses.reduce((a,b)=> a+b,0)


    let mode = "ckmeans"
    let legend_label = "Flux principaux"
    let legend_unit = "("+unit_label+"/jour)"
    let colors = c_gradient_reds
    let sources = Object.keys(this.props.territory.sources).includes("emd") ? ["emd"] : ["entd", "census", "mobpro", "bpe"]

    let legend_values = flows_masses

    // --- create layers
    let communes_layer = createCommuneBordersLayer(communes)
    let flows_layer = createFlowsLayer(flows_coords, flows_masses, flows_labels, mode, colors);

    let [legend_intervals, legend_colors] = getLegendMode(mode, legend_values, colors)
    let legend = [
      {type: "LegendCursor", params: {min: 25,
                                      max: 200,
                                      step: 25,
                                      id: "flows_od",
                                      value: flows_limit,
                                      cursorFunction: this.selectFlowsLimit.bind(this)}},
      {type: "LegendDescription", params: {desc: "Seuls les " + flows_limit + " flux les plus importants sont affichés.  Ils représentent " + formatFigure(total_flows_masses_displayed/total_flows*100, 2) + "% " + unit_legend + "."}},
      {type: "LegendSpace", params: {}},
      {type: "LegendLabel", params: {label: legend_label, unit: legend_unit}},
      {type: "LegendValuesFlows", params: {intervals: legend_intervals, colors: legend_colors}},
    ]

    let layer_to_fit = communes_layer
    let layers = [communes_layer, flows_layer]

    layers.push(createCommunesNamesLayerEasy(communes))

    let sources_map = sources
    return {unit, unit_label, unit_legend, flows_limit, layer_to_fit, layers, legend, sources_map}
  }

  getCommunesTable(unit, unit_label, unit_legend){
    let territory = this.props.territory
    let communes = territory.communes;

    /* Geocode to Name and Coords DICT */
    let geo_code_dict = territory.geo_code_dict;
    if(geo_code_dict == null){
      geo_code_dict = {}
    }
    let all_communes = communes.concat(territory.influence_communes).concat(territory.work_communes)
    all_communes.map((c)=>geo_code_dict[c.geo_code] = {"center": c.center, "name": c.name})

    /* FLOWS */
    let flows_od = territory.travels_analysis["3_flows"].flows_commune_all[unit];
    flows_od.sort((a,b)=> b[2] - a[2])

    let flows_od_table = []
    flows_od.forEach((f, i) =>
      flows_od_table.push({
        geo_code_ori: f[0],
        name_ori: geo_code_dict[f[0]]["name"],
        geo_code_des: f[1],
        name_des: geo_code_dict[f[1]]["name"],
        flow: f[2],
      })
    )

    let headlines=["Code Insee A", "Commune A", "Code Insee B", "Commune B", "Flux A↔B (" + unit_label + "/jour)"]
    let rows = flows_od_table.map((f)=> Object.values(f))
    let format_table=[(f)=>f, (f)=>f, (f)=>f, (f)=>f, (f)=>formatFigure(f, 3)]
    let format_csv=[(f)=>f, (f)=>f, (f)=>f, (f)=>f, (f)=>f.toPrecision(3).toString().replace(".", ",")]
    let align=["l", "l", "l", "l", "r"]

    let sources_table = Object.keys(this.props.territory.sources).includes("emd") ? ["emd"] : ["entd", "census", "mobpro", "bpe"]
    let name_csv= "flux_entre_communes_" + unit_label

    return {headlines, rows, align, format_table, format_csv, sources_table, name_csv}
  }

  constructor(props) {
    super(props);
    let unit_init = "distance"
    let label_init = "km"
    let legend_init = "de la distance totale"
    let flows_limit_init = 50

    this.state = Object.assign({}, {
      viewMap: true,
      viewTable: false,
    },
    this.getCommunesMap(unit_init, label_init, legend_init, flows_limit_init),
    this.getCommunesTable(unit_init, label_init, legend_init))
  }

  setView = (view) => {
      this.setState({
        viewMap: view=="map",
        viewTable: view=="table",
      })
  }
  setUnit = (unit, label, legend) => {
    this.setState(function(prevState, prevProps){
      this.setState(this.getCommunesMap(unit, label, legend, prevState.flows_limit))
    })
    this.setState(this.getCommunesTable(unit, label, legend))
  }
  selectFlowsLimit = (flows_limit) => {
      this.setState(function(prevState, prevProps){
        return this.getCommunesMap(prevState.unit, prevState.unit_label, prevState.unit_legend, flows_limit)
      })
  }

  componentDidMount() {
    // --- init map
    let mymap = this.mymap = getMyMap("flows_od", true, 0.3);
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
    let unit_list = [{selected: "distance", label_button: "Distance parcourue", label_unit: "km", label_legend: "de la distance totale"},
                     {selected: "number", label_button: "Nombre de déplacements", label_unit: "déplacements", label_legend: "du nombre total de déplacements" },
                     {selected: "ghg_emissions", label_button: "Emissions de GES", label_unit: "tCO2eq", label_legend: "des émissions totales"}]

    return(
          <div className="row content mt-4 mb-5">
            <div className="col">

                <div className="row">
                  <div className="col-12">
                    <h3 className="mb-3">principaux flux entre communes</h3>
                  </div>
                </div>

                <div className="row mt-1 mb-2">
                  {unit_list.map((u) =>
                    <div className="col-auto pr-1">
                      <p onClick={this.setUnit.bind(this, u.selected, u.label_unit, u.label_legend)}
                         className={this.state.unit == u.selected ? "button p-1 pl-2 pr-2 active" : "button p-1 pl-2 pr-2"}>{u.label_button}</p>
                    </div>
                  )}
                </div>

              <div className="row">
                <div className="col-12" style={{display: this.state.viewMap ? "block" : "none"}}>
                  <LeafletMapLegend legend={this.state.legend}
                                    all_sources={this.props.territory.sources}
                                    concerned_sources={this.state.sources_map}
                                    id="flows_od"
                                    height="600px"/>
                </div>

                <div className="col-12" style={{display: this.state.viewTable ? "block" : "none"}}>
                 <Table headlines={this.state.headlines}
                        rows={this.state.rows}
                        align={this.state.align}
                        format={this.state.format_table}
                        all_sources={this.props.territory.sources}
                        concerned_sources={this.state.sources_table}
                        height="600px"/>
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

export default FlowsOD_all;
