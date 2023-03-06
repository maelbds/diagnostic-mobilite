import React, { Component } from 'react';

import getMyMap, {getLegendMode} from '../b-LeafletMap/leaflet_map';
import {createCommuneBordersLayer, getCommunesMassElements} from '../b-LeafletMap/LeafletMapElement/createCommune';
import {createCommunesNamesLayerEasy} from '../b-LeafletMap/LeafletMapElement/createCommuneName';
import {createGridLayer} from '../b-LeafletMap/LeafletMapElement/createGrid';
import {createCyclePath} from '../b-LeafletMap/LeafletMapElement/createCyclePath';
import {createPlacesLayer} from '../b-LeafletMap/LeafletMapElement/createPlaceLayer';

import LeafletMapLegend from '../b-LeafletMap/LeafletMapLegend';
import Info from '../f-Utilities/Info';
import Table from '../d-Table/Table';
import SourcesRow from '../f-Utilities/SourcesRow';
import ViewButton from '../f-Utilities/ViewButton';
import DownloadButton from '../f-Utilities/DownloadButton';
import DataSelectionButton from '../f-Utilities/DataSelectionButton';

import {c_missing_data, c_gradient_greens, c_yellow} from '../a-Graphic/Colors';
import {pattern_shared_cycle_paths, pattern_dedicated_cycle_paths, p_size_0} from '../a-Graphic/Layout';
import {formatFigure, downloadCSV, cols_to_rows, titleCase} from '../f-Utilities/util_func';

class CyclingFacilities extends React.Component {
  getCommunesMap(selected){
    /* COMMUNES */
    let communes = this.props.territory.communes;
    let communes_coords = communes.map((c) => c.center);
    let communes_names = communes.map((c) => c.name);


    // BACKGROUND
    if(selected == "borders"){
      let communes_layer = createCommuneBordersLayer(communes)
      var layer_to_fit = communes_layer
      var layers = [communes_layer]
      var sources = []
      var legend = []
    }
    else if(selected == "cycle_paths_length_per_hab"){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "ckmeans",
        legend_label: "Longueur de voie cyclable par habitant.e",
        legend_unit: "(m/hab)",
        colors: c_gradient_greens,
        sources: ["transportdatagouv_cycle_paths", "dossier_complet"],
        indicatorFunction: (c) => c.cycle_paths_length_per_hab,
        massFunction: (c) => c.cycle_paths_length_per_hab,
        labelFunction: (c) => c.name + " - " + formatFigure(c.cycle_paths_length_per_hab, 2) + "m/hab",
      })
    }
    else if(selected == "gridded_pop"){
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

    /* CYCLE PATHS */
    let cycle_paths = this.props.territory.cycle_paths;

    let dedicated_ame = ["PISTE CYCLABLE", "DOUBLE SENS CYCLABLE PISTE", "VOIE VERTE", "VELO RUE", "COULOIR BUS+VELO"]
    let shared_ame = ["BANDE CYCLABLE", "DOUBLE SENS CYCLABLE BANDE", "DOUBLE SENS CYCLABLE NON MATERIALISE",
                      "AMENAGEMENT MIXTE PIETON VELO HORS VOIE VERTE", "CHAUSSEE A VOIE CENTRALE BANALISEE"]

    let dedicated_cycle_paths = cycle_paths.filter((p)=> dedicated_ame.includes(p.ame_d) | dedicated_ame.includes(p.ame_g))
    let shared_cycle_paths = cycle_paths.filter((p)=> shared_ame.includes(p.ame_d) | shared_ame.includes(p.ame_g))

    function name_ame(ame_g, ame_d){
      if (ame_g == "AUCUN"){
        return titleCase(ame_d)
      } else if (ame_d == "AUCUN"){
        return titleCase(ame_g)
      } else {
        return titleCase(ame_d) + " & " + titleCase(ame_g)
      }
    }
    let dedicated_cycle_paths_geom = dedicated_cycle_paths.map((a) => a.geometry)
    let dedicated_cycle_paths_names = dedicated_cycle_paths.map((a) => name_ame(a.ame_g, a.ame_d) + " </br><i>(mis à jour le " + a.date_maj + ")</i>")

    let shared_cycle_paths_geom = shared_cycle_paths.map((a) => a.geometry)
    let shared_cycle_paths_names = shared_cycle_paths.map((a) => name_ame(a.ame_g, a.ame_d) + " </br><i>(mis à jour le " + a.date_maj + ")</i>")

    layers.push(createCyclePath(dedicated_cycle_paths_geom, dedicated_cycle_paths_names, pattern_dedicated_cycle_paths))
    layers.push(createCyclePath(shared_cycle_paths_geom, shared_cycle_paths_names, pattern_shared_cycle_paths))
    legend.push({type: "LegendSpace", params: {}})
    legend.push({type: "LegendLabel", params: {label: "Voie cyclable"}})
    legend.push({type: "LegendCyclePath", params: {name: "Voie dédiée", pattern: pattern_dedicated_cycle_paths}})
    legend.push({type: "LegendCyclePath", params: {name: "Voie partagée", pattern: pattern_shared_cycle_paths}})
    sources.push("transportdatagouv_cycle_paths")


    /* CYCLE PARKINGS */
    let cycle_parkings = this.props.territory.cycle_parkings;

    function name_parkings(capacite, gestionnaire, date_maj){
      let cap = capacite==null ? "/" : capacite
      let ges = gestionnaire==null ? "/" : gestionnaire
      return cap + " places " + "</br><i>(mis à jour le " + date_maj + ")</i>"
    }
    let cycle_parkings_coords = cycle_parkings.map((cp) => [cp.lat, cp.lon])
    let cycle_parkings_labels = cycle_parkings.map((cp) => name_parkings(cp.capacite, cp.gestionnaire, cp.date_maj))

    layers.push(createPlacesLayer(cycle_parkings_coords, p_size_0/2, c_yellow, cycle_parkings_labels))
    legend.push({type: "LegendSpace", params: {}})
    legend.push({type: "LegendPlace", params: {label: "Stationnement vélo", color: c_yellow, size: p_size_0+4}})
    sources.push("transportdatagouv_cycle_parkings")

    sources = [...new Set(sources)];


    layers.push(createCommunesNamesLayerEasy(communes))

    let sources_map = sources
    return {selected, layer_to_fit, layers, legend, sources_map}
  }

  getCommunesTable(){
    let communes = this.props.territory.communes;

    let headlines=["Code Insee", "Commune", "Longueur totale de voies cyclables (km)", "Longueur de voie cyclable/hab (m/hab)"]
    let cols=[communes.map((c)=> c.geo_code),
              communes.map((c)=> c.name),
              communes.map((c)=> c.cycle_paths_length != null ? Math.round(c.cycle_paths_length/1000) : null),
              communes.map((c)=> c.cycle_paths_length_per_hab != null ? c.cycle_paths_length_per_hab : null)]
    let format_table=[(f)=>f,
                (f)=>f,
                (f)=>formatFigure(f),
                (f)=>formatFigure(f, 2)]
    let format_csv=[(f)=>f,
                (f)=>f,
                (f)=>formatFigure(f),
                (f)=>formatFigure(f, 2)]
    let align=["l", "l", "r", "r"]

    let rows = cols_to_rows(cols)
    let sources_table = ["dossier_complet", "transportdatagouv_cycle_paths"]
    let name_csv= "cyclabilite"
    return {headlines, rows, align, format_table, format_csv, sources_table, name_csv}
  }


  constructor(props) {
    super(props);
    let selected_init = "borders"

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
    let mymap = this.mymap = getMyMap("cycle_paths", true, 0.3);
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
    let data_list = [{selected: "borders", label: "contour des communes"},
                     {selected: "cycle_paths_length_per_hab", label: "longueur de voie cyclable par habitant.e"},
                     {selected: "gridded_pop", label: "population carroyée"}]

    return(
          <div className="row content mt-4 mb-5">

            <div className="col-3">
                <div className="row">
                  <div className="col-12">
                    <h3 className="mb-3">infrastructures cyclables</h3>
                  </div>
                </div>

                <div className="row">
                  <div className="col-12 line-border">
                    <p className="mb-2"><i>fond de carte :</i></p>
                    {data_list.map((d)=>
                      <DataSelectionButton selected={this.state.selected === d.selected}
                                           display_category={this.displayCategory.bind(this, d.selected)} label={d.label} />
                    )}
                  </div>
                </div>

                <div className="row mt-5">
                  <div className="col-12">
                    <p className="mb-1">La longueur de voie cyclable est la somme des linéaires de toutes les voies cyclables (dédiées et partagées). <Info content="Pour une voie cyclable à double sens, la longueur de la voie en question est doublée." /></p>

                      <p className="mb-1">La longueur de voie cyclable par habitant.e est calculée pour chaque commune en calculant la longueur des voies cyclables
                      au sein de la commune puis en divisant par la population de la commune.</p>
                  </div>
                </div>
            </div>

            <div className="col-9">
              <div className="row">
                <div className="col-12" style={{display: this.state.viewMap ? "block" : "none"}}>
                  <LeafletMapLegend legend={this.state.legend}
                                    all_sources={this.props.territory.sources}
                                    concerned_sources={this.state.sources_map}
                                    id="cycle_paths"
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

export default CyclingFacilities;
