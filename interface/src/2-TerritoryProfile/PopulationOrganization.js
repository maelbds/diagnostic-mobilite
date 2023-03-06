import React, { Component } from 'react';

import getMyMap, {getLegendMode} from '../b-LeafletMap/leaflet_map';
import {createCommunesLayer, createCommunesMassLayer, createCommuneBordersLayer, getCommunesMassElements} from '../b-LeafletMap/LeafletMapElement/createCommune';
import {createCommunesNamesLayerEasy} from '../b-LeafletMap/LeafletMapElement/createCommuneName';
import {createGridLayer} from '../b-LeafletMap/LeafletMapElement/createGrid';
import {createPointsMassLayer} from '../b-LeafletMap/LeafletMapElement/createPoint';

import LeafletMapLegend from '../b-LeafletMap/LeafletMapLegend';
import Info from '../f-Utilities/Info';
import Table from '../d-Table/Table';
import SourcesRow from '../f-Utilities/SourcesRow';
import ViewButton from '../f-Utilities/ViewButton';
import DownloadButton from '../f-Utilities/DownloadButton';
import DataSelectionButton from '../f-Utilities/DataSelectionButton';

import {c_missing_data, c_gradient_greens, c_gradient_reds_greens, c_yellow} from '../a-Graphic/Colors';
import {formatFigure, downloadCSV, cols_to_rows} from '../f-Utilities/util_func';

class PopulationOrganization extends React.Component {
  getCommunesMap(selected){
    /* COMMUNES */
    let communes = this.props.territory.communes;
    let communes_coords = communes.map((c) => c.center);
    let communes_names = communes.map((c) => c.name);

    if(selected == "population"){
      let communes_pop = communes.sort((a, b)=> b.population - a.population)
      let communes_pop_coords = communes_pop.map((c) => c.center);
      let communes_pop_masses = communes_pop.map((c) => c.population);
      let communes_pop_labels = communes_pop.map((c) => c.name + " - " + formatFigure(c.population) + " hab");

      let color = c_yellow

      let communes_layer = createCommuneBordersLayer(communes);
      let communes_pop_layer = createPointsMassLayer(communes_pop_coords, communes_pop_masses, communes_pop_labels, color);

      var sources = ["dossier_complet"]

      let legend_label = "Population"
      let legend_unit = ""

      var legend = [
        {type: "LegendPointMass", params: {label: legend_label, unit: legend_unit, color: color}}
      ]

      var layer_to_fit = communes_layer
      var layers = [communes_layer, communes_pop_layer]
    }
    else if(selected == "corrected_density"){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "ckmeans",
        legend_label: "Densité corrigée",
        legend_unit: "(hab/km² urbanisé)",
        colors: c_gradient_greens, // double slice to make a copy
        sources: ["dossier_complet", "surface", "artificialisation_rate"],
        indicatorFunction: (c) => c.corrected_density,
        massFunction: (c) => c.corrected_density,
        labelFunction: (c) => c.name + " - " + formatFigure(c.corrected_density, 3) + " hab/km² urbanisé",
      })
    }
    else if(selected == "gridded_population"){
      let gridded_population = [].concat(...communes.map((c)=>c.gridded_population));
      let gridded_pop_coords = gridded_population.map((c) => c.coords);
      let gridded_pop_masses = gridded_population.map((c) => c.population);
      let gridded_pop_labels = gridded_population.map((c) => formatFigure(c.population) + " hab");

      var legend_values = gridded_pop_masses
      var missing_data = false

      let mode = "ckmeans"
      let legend_label = "Population au carreau"
      let legend_unit = "(hab)"
      let colors = c_gradient_greens

      var sources = ["gridded_pop"]

      let communes_layer = createCommuneBordersLayer(communes);
      let gridded_incomes_layer = createGridLayer(gridded_pop_coords, gridded_pop_masses, gridded_pop_labels, mode, colors);

      let [legend_intervals, legend_colors] = getLegendMode(mode, legend_values, colors)
      var legend = [
        {type: "LegendLabel", params: {label: legend_label, unit: legend_unit}},
        {type: "LegendValues", params: {intervals: legend_intervals, colors: legend_colors, missing_data: missing_data}}
      ]

      var layer_to_fit = communes_layer
      var layers = [communes_layer, gridded_incomes_layer]
    }
    else if(selected == "gridded_population_hh"){
      let gridded_population = [].concat(...communes.map((c)=>c.gridded_population));
      let gridded_pop_coords = gridded_population.map((c) => c.coords);
      let gridded_pop_masses = gridded_population.map((c) => Math.round(c.population/c.households*10)/10);
      let gridded_pop_labels = gridded_population.map((c) => formatFigure(Math.round(c.population/c.households*10)/10) + " hab/ménage");

      var legend_values = gridded_pop_masses
      var missing_data = false

      let mode = "gridded_pop_hh"
      let legend_label = "Taille moyenne des ménages au carreau"
      let legend_unit = "(hab/ménage)"
      let colors = c_gradient_reds_greens.slice(3, 9)

      var sources = ["gridded_pop"]

      let communes_layer = createCommuneBordersLayer(communes);
      let gridded_incomes_layer = createGridLayer(gridded_pop_coords, gridded_pop_masses, gridded_pop_labels, mode, colors);

      let [legend_intervals, legend_colors] = getLegendMode(mode, legend_values, colors)
      var legend = [
        {type: "LegendLabel", params: {label: legend_label, unit: legend_unit}},
        {type: "LegendValues", params: {intervals: legend_intervals, colors: legend_colors, missing_data: missing_data}}
      ]

      var layer_to_fit = communes_layer
      var layers = [communes_layer, gridded_incomes_layer]
    }
    else if(selected == "gridded_population_surf"){
      let gridded_population = [].concat(...communes.map((c)=>c.gridded_population));
      let gridded_pop_coords = gridded_population.map((c) => c.coords);
      let gridded_pop_masses = gridded_population.map((c) => Math.round(c.sum_hh_surface/c.population));
      let gridded_pop_labels = gridded_population.map((c) => formatFigure(Math.round(c.sum_hh_surface/c.population)) + " m²/hab");

      var legend_values = gridded_pop_masses
      var missing_data = false

      let mode = "gridded_pop_hh_surf"
      let legend_label = "Surface moyenne par personne carreau"
      let legend_unit = "(m²/hab)"
      let colors = c_gradient_reds_greens.slice(2, 8)

      var sources = ["gridded_pop"]

      let communes_layer = createCommuneBordersLayer(communes);
      let gridded_incomes_layer = createGridLayer(gridded_pop_coords, gridded_pop_masses, gridded_pop_labels, mode, colors);

      let [legend_intervals, legend_colors] = getLegendMode(mode, legend_values, colors)
      var legend = [
        {type: "LegendLabel", params: {label: legend_label, unit: legend_unit}},
        {type: "LegendValues", params: {intervals: legend_intervals, colors: legend_colors, missing_data: missing_data}}
      ]

      var layer_to_fit = communes_layer
      var layers = [communes_layer, gridded_incomes_layer]
    }

    layers.push(createCommunesNamesLayerEasy(communes))
    let sources_map = sources

    return {selected, layer_to_fit, layers, legend, sources_map}
  }

  getCommunesTable(){
    let communes = this.props.territory.communes;

    let headlines=["Code Insee", "Commune", "Population", "Densité (hab/km²)", "Densité corrigée (hab/km²)"]
    let cols=[communes.map((c)=> c.geo_code),
              communes.map((c)=> c.name),
              communes.map((c)=> c.population != null ? c.population : null),
              communes.map((c)=> c.density != null ? c.density : null),
              communes.map((c)=> c.corrected_density != null ? c.corrected_density : null)]
    let align=["l", "l", "r", "r", "r"]
    let format_table=[(f)=>f,
                (f)=>f,
                (f)=>formatFigure(f),
                (f)=>formatFigure(f,3),
                (f)=>formatFigure(f,3)]
    let format_csv=[(f)=>f,
                (f)=>f,
                (f)=>f,
                (f)=>Math.round(f),
                (f)=>Math.round(f)]

    let rows = cols_to_rows(cols)
    let name_csv= "population_densite"
    let sources_table = ["dossier_complet", "surface", "artificialisation_rate"]
    return {headlines, rows, align, format_table, format_csv, name_csv, sources_table}
  }


  constructor(props) {
    super(props);
    let selected_init = "population"
    this.state = Object.assign({}, {
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
    let mymap = this.mymap = getMyMap("population_organization", true, 0.3);
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
    let data_list = [{selected: "population", label: "population"},
                     {selected: "corrected_density", label: "densité corrigée"},
                     {selected: "gridded_population", label: "population carroyée"},
                     {selected: "gridded_population_hh", label: "taille moyenne des ménages au carreau"},
                     {selected: "gridded_population_surf", label: "surface moyenne par personne au carreau"}]

    return(
          <div className="row content mt-4 mb-5">

            <div className="col-3">
                <div className="row">
                  <div className="col-12">
                    <h3 className="mb-3">organisation géographique de la population</h3>
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
                    <p className="mb-2">La densité corrigée est basée sur la surface urbanisée uniquement.
                    Elle représente la manière dont la population occupe les sols.</p>

                    <p className="mb-2">La population carroyée est la population par carreau de 200m de côté.</p>
                    <p>La taille des ménages est en moyenne de <b>2.2</b> en France. <Info content="La taille des ménages au carreau est le rapport entre la population et le nombre de ménage du carreau."/></p>
                  </div>
                </div>
            </div>

            <div className="col-9">
              <div className="row">
                <div className="col-12" style={{display: this.state.viewMap ? "block" : "none"}}>
                  <LeafletMapLegend legend={this.state.legend}
                                    all_sources={this.props.territory.sources}
                                    concerned_sources={this.state.sources_map}
                                    id="population_organization"
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

export default PopulationOrganization;
