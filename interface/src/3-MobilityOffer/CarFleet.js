import React, { Component } from 'react';

import getMyMap, {getLegendMode} from '../b-LeafletMap/leaflet_map';
import {createCommunesNamesLayerEasy} from '../b-LeafletMap/LeafletMapElement/createCommuneName';
import {createCommunesMassLayer, createCommunesLayer} from '../b-LeafletMap/LeafletMapElement/createCommune';
import {createZFE} from '../b-LeafletMap/LeafletMapElement/createZFE';

import Legend from '../b-LeafletMap/Legend/Legend';
import Info from '../f-Utilities/Info';
import SourcesRow from '../f-Utilities/SourcesRow';
import Table from '../d-Table/Table';
import ViewButton from '../f-Utilities/ViewButton';
import DownloadButton from '../f-Utilities/DownloadButton';
import DataSelectionButton from '../f-Utilities/DataSelectionButton';

import {c_missing_data, c_gradient_greens} from '../a-Graphic/Colors';
import {pattern_zfe} from '../a-Graphic/Layout';
import {formatFigure, downloadCSV, cols_to_rows} from '../f-Utilities/util_func';

class CarFleet extends React.Component {
  sort_labels(labels){
    let labels_order = {
      "elec" : 7,
      "critair1" : 6,
      "critair2": 5,
      "critair3": 4,
      "critair4": 3,
      "critair5": 1,
      "nc": 0
    };
    function comparison(mean1, mean2){
      return labels_order[mean2] - labels_order[mean1]
    }
    return labels.sort(comparison)
  }

  getCommunesMap(selected){
    /* COMMUNES */
    let communes = this.props.territory.communes;
    let communes_coords = communes.map((c) => c.center);
    let communes_names = communes.map((c) => c.name);

    // Car Fleet
    let communes_wd = communes.filter((c) => c.critair != null)
    let selected_labels = this.sort_labels(selected).map((s)=>communes_wd[0].critair[s].label).join(", ")

    let communes_total_veh = communes_wd.map((c)=>Object.keys(c.critair).map(
        (crit) => c.critair[crit]["value"]).reduce((a, b) => a + b, 0))
    let communes_selected_veh = communes_wd.map((c)=> Object.keys(c.critair).filter(
      (crit) => selected.includes(crit)).map(
        (crit) => c.critair[crit]["value"]).reduce((a, b) => a + b, 0))
    let communes_selected_prop = communes_wd.map((c, i)=> Math.round(communes_selected_veh[i]/communes_total_veh[i]*100))
    let communes_labels = communes_wd.map((c, i) => "<b>" + c.name + "</b></br>" + formatFigure(communes_selected_veh[i]) + " véhicules " + selected_labels + "</br><i>" + communes_selected_prop[i] + "% du parc</i>");

    let communes_nd = communes.filter((c) => c.critair == null)
    let communes_nd_labels = communes_nd.map((c) => c.name);


    let mode = "ckmeans"
    let legend_label = "Part des véhicules " + selected_labels
    let legend_unit = "(%)"
    let colors = c_gradient_greens

    let communes_layer = createCommunesMassLayer(communes_wd, communes_selected_prop, communes_labels, mode, colors);
    let communes_layer_nd = createCommunesLayer(communes_nd, communes_nd_labels, c_missing_data);

    let legend_values = communes_selected_prop
    let missing_data = communes_nd.length > 0

    let [legend_intervals, legend_colors] = getLegendMode(mode, legend_values, colors)
    var legend = [
      {type: "LegendLabel", params: {label: legend_label, unit: legend_unit}},
      {type: "LegendValues", params: {intervals: legend_intervals, colors: legend_colors, missing_data: missing_data}}
    ]

    // ZFE
    function name_zfe(date_debut, date_fin, vp_critair, vp_horaires){
      let vp_crit = vp_critair==null ? "/" : vp_critair
      let vp_hor = vp_horaires==null ? "" : "(" + vp_horaires + ")"
      if (date_fin=="None"){
        return "<b>ZFE en vigueur à partir du " + date_debut + " </b></br>Les véhicules particuliers avec une vignette " + vp_crit + " et au-delà ne peuvent pas circuler " + vp_hor
      } else {
        return "<b>ZFE en vigueur entre le " + date_debut + " et le " + date_fin + " </b></br>Les véhicules particuliers avec une vignette " + vp_crit + " et au-delà ne peuvent pas circuler " + vp_hor
      }
    }
    let zfe_layers = [];
    for (let z of this.props.territory.zfe){
      zfe_layers.push(createZFE(z.geometry, name_zfe(z.date_debut, z.date_fin, z.vp_critair, z.vp_horaires)))
    }
    if (zfe_layers.length > 0){
      legend.unshift({type: "LegendSpace", params:{}})
      legend.unshift({type: "LegendZFE", params:{name: "Périmètre ZFE", pattern: pattern_zfe}})
    }

    // ALL

    let layer_to_fit = communes_layer.addLayer(communes_layer_nd)
    let layers = [communes_layer, communes_layer_nd].concat(zfe_layers)

    let sources = ["critair", "transportdatagouv_zfe"]

    layers.push(createCommunesNamesLayerEasy(communes))

    return {selected, layer_to_fit, layers, legend, sources}
  }

  getCommunesTable(){
    let communes = this.props.territory.communes;
    let communes_wd = communes.filter((c) => c.critair != null)
    let critair_labels = {};
    this.sort_labels(Object.keys(communes_wd[0].critair)).map((key) => critair_labels[key] = communes_wd[0].critair[key]["label"])

    let headlines=["Code Insee", "Commune"]
    Object.values(critair_labels).map((label) => headlines.push(label))

    let cols=[communes.map((c)=> c.geo_code),
              communes.map((c)=> c.name)]
    Object.keys(critair_labels).map((key) => cols.push(communes.map((c)=> c.critair[key]["value"] != null ? c.critair[key]["value"] : null)))

    let format_table=[(f)=>f, (f)=>f]
    Object.keys(critair_labels).map((key) => format_table.push((f)=>formatFigure(f)))

    let format_csv=[(f)=>f, (f)=>f]
    Object.keys(critair_labels).map((key) => format_csv.push((f)=>f))

    let align=["l", "l"]
    Object.keys(critair_labels).map((key) => align.push("r"))

    let name_csv = "parc_vehicules_(nb)"

    let rows = cols_to_rows(cols)
    return {headlines, rows, align, format_table, format_csv, name_csv}
  }

  constructor(props) {
    super(props);
    let selected_init = ["critair1", "critair2", "elec"]

    this.state = Object.assign({},{
        viewMap: true,
        viewTable: false,
      },
      this.getCommunesTable(),
      this.getCommunesMap(selected_init));
  }

  setView = (view) => {
      this.setState({
        viewMap: view=="map",
        viewTable: view=="table",
      })
  }
  displayCategory = (selected) => {
    this.setState(function(prevState, prevProps) {
      let index = prevState.selected.indexOf(selected);
      let new_selected = [];
      if (index > -1) {
        new_selected = prevState.selected
        new_selected.splice(index, 1) // 2nd parameter means remove one item only
      }
      else{
        new_selected = prevState.selected.concat([selected])
      }
      return this.getCommunesMap(new_selected)
    })
    this.setState({viewMap: true, viewTable: false})
  }

  componentDidMount() {
    // --- init map
    let mymap = this.mymap = getMyMap("car_fleet", true, 0.3);
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
     let communes = this.props.territory.communes;
     let communes_wd = communes.filter((c) => c.critair != null)
     let critair_labels = {};
     this.sort_labels(Object.keys(communes_wd[0].critair)).map((key) => critair_labels[key] = communes_wd[0].critair[key]["label"])

    return(
          <div className="row content mt-4 mb-5">

            <div className="col-3">
                <div className="row">
                  <div className="col-12">
                    <h3 className="mb-3">parc de véhicules</h3>
                  </div>
                </div>

                <div className="row">
                  <div className="col-12 line-border">
                     <p className="mb-2"><i>Vignettes Crit'Air :</i></p>

                     {Object.keys(critair_labels).map((critair_key, i)=>
                       <div className="form-check">
                         <input className="form-check-input ml-0 mt-2" type="checkbox" value={critair_key} id={"defaultCheck" + i}
                         checked={this.state.selected.includes(critair_key)}
                         onChange={ this.displayCategory.bind(this, critair_key) }  />
                         <label className="form-check-label" for={"defaultCheck" + i}>
                           <p>{critair_labels[critair_key]}</p>
                         </label>
                        </div>
                     )}

                  </div>
                </div>
            </div>

            <div className="col-9">
              <div className="row">
                <div className="col-12" style={{display: this.state.viewMap ? "block" : "none"}}>
                  <div className="row align-items-end">
                    <div className="col-10">
                      <div style={{height: "500px"}} id="car_fleet"></div>
                    </div>
                    <div className="col-2 pl-0 pr-0">
                        <Legend legend={this.state.legend} />
                    </div>
                  </div>
                </div>

                <div className="col-12" style={{display: this.state.viewTable ? "block" : "none"}}>
                 <Table headlines={this.state.headlines}
                        rows={this.state.rows}
                        align={this.state.align}
                        format={this.state.format_table}
                        height="500px"/>
                </div>
              </div>

              <SourcesRow sources={this.props.territory.sources} concerned={this.state.sources}/>

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

export default CarFleet;
