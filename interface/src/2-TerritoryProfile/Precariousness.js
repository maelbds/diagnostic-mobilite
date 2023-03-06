import React, { Component } from 'react';

import getMyMap, {getLegendMode} from '../b-LeafletMap/leaflet_map';
import {createCommunesLayer, createCommunesMassLayer, createCommuneBordersLayer, getCommunesMassElements} from '../b-LeafletMap/LeafletMapElement/createCommune';
import {createCommunesNamesLayerEasy} from '../b-LeafletMap/LeafletMapElement/createCommuneName';
import {createGridLayer} from '../b-LeafletMap/LeafletMapElement/createGrid';

import LeafletMapLegend from '../b-LeafletMap/LeafletMapLegend';
import Info from '../f-Utilities/Info';
import Table from '../d-Table/Table';
import SourcesRow from '../f-Utilities/SourcesRow';
import ViewButton from '../f-Utilities/ViewButton';
import DownloadButton from '../f-Utilities/DownloadButton';
import DataSelectionButton from '../f-Utilities/DataSelectionButton';

import {c_missing_data, c_gradient_reds_greens} from '../a-Graphic/Colors';
import {formatFigure, downloadCSV, cols_to_rows} from '../f-Utilities/util_func';

class Precariousness extends React.Component {
  getCommunesMap(selected){
    /* COMMUNES */
    let communes = this.props.territory.communes;
    let communes_coords = communes.map((c) => c.center);
    let communes_names = communes.map((c) => c.name);

    if(selected == "fuel"){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "fuel",
        legend_label: "Part des ménages en précarité énergétique",
        legend_unit: "(%)",
        colors: c_gradient_reds_greens.slice(2, 8).slice().reverse(),
        sources: ["precariousness"],
        indicatorFunction: (c) => c.precariousness.fuel,
        massFunction: (c) => c.precariousness.fuel,
        labelFunction: (c) => c.name + " - " + c.precariousness.fuel + " %",
      })
    }
    else if(selected == "fuel_housing"){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "fuel_housing",
        legend_label: "Part des ménages en précarité énergétique",
        legend_unit: "(%)",
        colors: c_gradient_reds_greens.slice(2, 8).slice().reverse(), // double slice to make a copy
        sources: ["precariousness"],
        indicatorFunction: (c) => c.precariousness.fuel_housing,
        massFunction: (c) => c.precariousness.fuel_housing,
        labelFunction: (c) => c.name + " - " + c.precariousness.fuel_housing + " %",
      })
    }

    layers.push(createCommunesNamesLayerEasy(communes))

    let sources_map = sources
    return {selected, layer_to_fit, layers, legend, sources_map}
  }

  getCommunesTable(){
    let communes = this.props.territory.communes;

    let headlines=["Code Insee", "Commune", "Part des ménages en précarité énergétique mobilité (%)", "Part des ménages en précarité énergétique mobilité ou logement (%)"]
    let cols=[communes.map((c)=> c.geo_code),
              communes.map((c)=> c.name),
              communes.map((c)=> c.precariousness.fuel != null ? c.precariousness.fuel : null),
              communes.map((c)=> c.precariousness.fuel_housing != null ? c.precariousness.fuel_housing : null)]
    let format_table=[(f)=>f,
                (f)=>f,
                (f)=>formatFigure(f),
                (f)=>formatFigure(f)]
    let format_csv=[(f)=>f,
                (f)=>f,
                (f)=>formatFigure(f),
                (f)=>formatFigure(f)]
    let align=["l", "l", "r", "r"]

    let rows = cols_to_rows(cols)
    let sources_table = ["precariousness"]
    return {headlines, rows, align, format_table, format_csv, sources_table}
  }


  constructor(props) {
    super(props);
    let selected_init = "fuel"

    this.state = Object.assign({}, {
      name_csv: "precarite_energetique",
      viewMap: true,
      viewTable: false,
    },
    this.getCommunesMap(selected_init),
    this.getCommunesTable());
  }

  setView = (view) => {
      this.setState({
        viewMap: view=="map",
        viewTable: view=="table",
      })
  }
  displayCategory = (selected) => {
      this.setState(this.getCommunesMap(selected))
      this.setState({viewMap: true, viewTable: false})
  }

  componentDidMount() {
    // --- init map
    let mymap = this.mymap = getMyMap("precariousness", true, 0.3);
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
    let data_list = [{selected: "fuel", label: "précarité énergétique mobilité"},
                     {selected: "fuel_housing", label: "précarité énergétique mobilité ou logement"}]

    return(
          <div className="row content mt-4 mb-5">

            <div className="col-3">
                <div className="row">
                  <div className="col-12">
                    <h3 className="mb-3">précarité énergétique</h3>
                  </div>
                </div>

                <div className="row">
                  <div className="col-12 line-border">
                    {data_list.map((d)=>
                      <DataSelectionButton selected={this.state.selected === d.selected}
                                           display_category={this.displayCategory.bind(this, d.selected)} label={d.label} />
                    )}
                  </div>
                </div>

                <div className="row mt-5">
                  <div className="col-12">
                    <p className="mb-1">La précarité énergétique mobilité concerne <b>13.8%</b> des ménages en France,
                    c'est <b>20.3%</b> pour la précarité énergétique mobilité et logement.
                    <Info content="Les ménages en situation de précarité énergétique sont les ménages sous le 3ème décile de revenu, dont les dépenses énergétiques pour le logement ou pour le carburant de la mobilité quotidienne sont supérieures à un seuil (4,5% des revenus pour les dépenses de carburant, et 8% des revenus pour les dépenses énergétiques du logement)" /></p>
                  </div>
                </div>
            </div>

            <div className="col-9">
              <div className="row">
                <div className="col-12" style={{display: this.state.viewMap ? "block" : "none"}}>
                  <LeafletMapLegend legend={this.state.legend}
                                    all_sources={this.props.territory.sources}
                                    concerned_sources={this.state.sources_map}
                                    id="precariousness"
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

export default Precariousness;
