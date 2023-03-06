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

import {c_missing_data, c_gradient_greens} from '../a-Graphic/Colors';
import {formatFigure, downloadCSV, cols_to_rows} from '../f-Utilities/util_func';

class PopulationProfile extends React.Component {
  getCommunesMap(selected){
    /* COMMUNES */
    let communes = this.props.territory.communes;
    let communes_coords = communes.map((c) => c.center);
    let communes_names = communes.map((c) => c.name);

    let dict_csp = {};
    Object.keys(communes[0].csp).filter((key)=> key != "csp8" && key != "total15+").
    map((key) => dict_csp[key] = "Part des " + communes[0].csp[key]["label"].toLowerCase() + " (parmi les +15 ans)")

    if(selected == "motorisation_rate"){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "ckmeans",
        legend_label: "Taux de motorisation des ménages",
        legend_unit: "(%)",
        colors: c_gradient_greens,
        sources: ["dossier_complet"],
        indicatorFunction: (c) => c.motorisation_rate,
        massFunction: (c) => c.motorisation_rate,
        labelFunction: (c) =>  c.name + " - " + formatFigure(c.motorisation_rate, 2) + "%",
      })
    }
    else if(selected == "-18_prop"){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "ckmeans",
        legend_label: "Part des 17 ans et moins",
        legend_unit: "(%)",
        colors: c_gradient_greens,
        sources: ["pop_age"],
        indicatorFunction: (c) => c.pop_age["-18"],
        massFunction: (c) => Math.round(c.pop_age["-18"]/c.population*100),
        labelFunction: (c) => c.name + " - " + formatFigure(c.pop_age["-18"]/c.population*100, 2) + "% soit " + formatFigure(c.pop_age["-18"]) + " personnes",
      })
    }
    else if(selected == "+65_prop"){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "ckmeans",
        legend_label: "Part des 65 ans et plus",
        legend_unit: "(%)",
        colors: c_gradient_greens,
        sources: ["pop_age"],
        indicatorFunction: (c) => c.pop_age["+65"],
        massFunction: (c) => Math.round(c.pop_age["+65"]/c.population*100),
        labelFunction: (c) => c.name + " - " + formatFigure(c.pop_age["+65"]/c.population*100, 2) + "% soit " + formatFigure(c.pop_age["+65"]) + " personnes",
      })
    }
    else if(selected == "employed_prop"){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "ckmeans",
        legend_label: "Part des actifs & actives",
        legend_unit: "(%)",
        colors: c_gradient_greens,
        sources: ["dossier_complet"],
        indicatorFunction: (c) => c.status.employed,
        massFunction: (c) => Math.round(c.status.employed/c.population*100),
        labelFunction: (c) => c.name + " - " + formatFigure(c.status.employed/c.population*100, 2) + "% soit " + formatFigure(c.status.employed) + " personnes",
      })
    }
    else if(selected == "retired_prop"){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "ckmeans",
        legend_label: "Part des personnes à la retraite",
        legend_unit: "(%)",
        colors: c_gradient_greens,
        sources: ["dossier_complet"],
        indicatorFunction: (c) => c.status.retired,
        massFunction: (c) => Math.round(c.status.retired/c.population*100),
        labelFunction: (c) => c.name + " - " + formatFigure(c.status.retired/c.population*100, 2) + "% soit " + formatFigure(c.status.retired) + " personnes",
      })
    }
    else if(selected == "scholars_inf_prop"){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "ckmeans",
        legend_label: "Part des scolaires de 17 ans et moins",
        legend_unit: "(%)",
        colors: c_gradient_greens,
        sources: ["dossier_complet"],
        indicatorFunction: (c) => c.status.scholars_11_14+c.status.scholars_15_17+c.status.scholars_2_5+c.status.scholars_6_10,
        massFunction: (c) => Math.round((c.status.scholars_11_14+c.status.scholars_15_17+c.status.scholars_2_5+c.status.scholars_6_10)/c.population*100),
        labelFunction: (c) => c.name + " - " + formatFigure(c.status.scholars_11_14+c.status.scholars_15_17+c.status.scholars_2_5+c.status.scholars_6_10/c.population*100, 2) + "% soit " + formatFigure(c.status.scholars_11_14+c.status.scholars_15_17+c.status.scholars_2_5+c.status.scholars_6_10) + " personnes",
      })
    }
    else if(selected == "scholars_sup_prop"){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "ckmeans",
        legend_label: "Part des scolaires de 18 ans et plus",
        legend_unit: "(%)",
        colors: c_gradient_greens,
        sources: ["dossier_complet"],
        indicatorFunction: (c) => c.status.scholars_18,
        massFunction: (c) => Math.round(c.status.scholars_18/c.population*100),
        labelFunction: (c) => c.name + " - " + formatFigure(c.status.scholars_18/c.population*100, 2) + "% soit " + formatFigure(c.status.scholars_18) + " personnes",
      })
    }
    else if(selected == "unemployed_prop"){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "ckmeans",
        legend_label: "Part des personnes au chômage",
        legend_unit: "(%)",
        colors: c_gradient_greens,
        sources: ["dossier_complet"],
        indicatorFunction: (c) => c.status.unemployed,
        massFunction: (c) => Math.round(c.status.unemployed/c.population*100),
        labelFunction: (c) => c.name + " - " + formatFigure(c.status.unemployed/c.population*100, 2) + "% soit " + formatFigure(c.status.unemployed) + " personnes",
      })
    }
    else if(Object.keys(dict_csp).includes(selected)){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "ckmeans",
        legend_label: dict_csp[selected],
        legend_unit: "(%)",
        colors: c_gradient_greens,
        sources: ["dossier_complet"],
        indicatorFunction: (c) => c.csp[selected].value,
        massFunction: (c) => Math.round(c.csp[selected].value/c.csp["total15+"].value*100),
        labelFunction: (c) => c.name + " - " + formatFigure(c.csp[selected].value/c.csp["total15+"].value*100, 2) + "% soit " + formatFigure(c.csp[selected].value) + " personnes",
      })
    }

    layers.push(createCommunesNamesLayerEasy(communes))

    let sources_map = sources
    return {selected, layer_to_fit, layers, legend, sources_map}
  }

  getCommunesTable(selected){
    let communes = this.props.territory.communes;

    let dict_csp = {};
    Object.keys(communes[0].csp).filter((key)=> key != "csp8" && key != "total15+").
    map((key) => dict_csp[key] = "Part des " + communes[0].csp[key]["label"].toLowerCase() + " (parmi les +15 ans)")

    if (["motorisation_rate"].includes(selected)){
      var headlines=["Code Insee", "Commune", "Taux de motorisation des ménages"]
      var cols=[communes.map((c)=> c.geo_code),
                communes.map((c)=> c.name),
                communes.map((c)=> c.motorisation_rate != null ? c.motorisation_rate : null)]
      var format_table=[(f)=>f, (f)=>f, (f)=>formatFigure(f, 2)]
      var format_csv=[(f)=>f, (f)=>f, (f)=>formatFigure(f)]
      var align=["l", "l", "r"]

      var rows = cols_to_rows(cols)
      var name_csv = "profil_motorisation"

      var sources_table = ["dossier_complet"]
    }
    else if(["-18_prop", "+65_prop"].includes(selected)){
      var headlines=["Code Insee", "Commune", "Population totale", "Population des 17 ans et moins", "Population des 65 ans et plus"]
      var cols=[communes.map((c)=> c.geo_code),
                communes.map((c)=> c.name),
                communes.map((c)=> c.population != null ? c.population : null),
                communes.map((c)=> c.pop_age["-18"] != null ? c.pop_age["-18"] : null),
                communes.map((c)=> c.pop_age["+65"] != null ? c.pop_age["+65"] : null)]
      var format_table=[(f)=>f,
                  (f)=>f,
                  (f)=>formatFigure(f),
                  (f)=>formatFigure(f),
                  (f)=>formatFigure(f)]
      var format_csv=[(f)=>f,
                  (f)=>f,
                  (f)=>f,
                  (f)=>f,
                  (f)=>f]
      var align=["l", "l", "r", "r", "r"]

      var rows = cols_to_rows(cols)
      var name_csv = "profil_age"

      var sources_table = ["pop_age"]
    }
    else if(["employed_prop", "retired_prop", "scholars_inf_prop", "scholars_sup_prop", "unemployed_prop"].includes(selected)){
      var headlines=["Code Insee", "Commune", "Population totale", "Population active", "Population retraitée", "Population scolaire (-17ans)", "Population scolaire (+18 ans)", "Population au chômage"]
      var cols=[communes.map((c)=> c.geo_code),
                communes.map((c)=> c.name),
                communes.map((c)=> c.population != null ? c.population : null),
                communes.map((c)=> c.status.employed != null ? c.status.employed : null),
                communes.map((c)=> c.status.retired != null ? c.status.retired : null),
                communes.map((c)=> c.status.scholars_11_14+c.status.scholars_15_17+c.status.scholars_2_5+c.status.scholars_6_10 != null ? c.status.scholars_11_14+c.status.scholars_15_17+c.status.scholars_2_5+c.status.scholars_6_10 : null),
                communes.map((c)=> c.status.scholars_18 != null ? c.status.scholars_18 : null),
                communes.map((c)=> c.status.unemployed != null ? c.status.unemployed : null)]
      var format_table=[(f)=>f,
                  (f)=>f,
                  (f)=>formatFigure(f),
                  (f)=>formatFigure(f),
                  (f)=>formatFigure(f),
                  (f)=>formatFigure(f),
                  (f)=>formatFigure(f),
                  (f)=>formatFigure(f)]
      var format_csv=[(f)=>f,
                  (f)=>f,
                  (f)=>f,
                  (f)=>f,
                  (f)=>f,
                  (f)=>f,
                  (f)=>f,
                  (f)=>f]
      var align=["l", "l", "r", "r", "r", "r", "r", "r"]

      var rows = cols_to_rows(cols)
      var name_csv = "profil_statut"

      var sources_table = ["dossier_complet"]
    }
    else if (Object.keys(dict_csp).includes(selected)) {
      var headlines=["Code Insee", "Commune"]
      Object.keys(communes[0].csp).filter((key)=>key != "csp8").map((key) => headlines.push(communes[0].csp[key]["label"]))

      var cols=[communes.map((c)=> c.geo_code),
                communes.map((c)=> c.name)]
      Object.keys(communes[0].csp).filter((key)=>key != "csp8").map((key) => cols.push(communes.map((c)=> c.csp[key].value != null ? c.csp[key].value : null)))

      var format_table=[(f)=>f,
                         (f)=>f]
      Object.keys(communes[0].csp).filter((key)=>key != "csp8").map((key) => format_table.push((f)=>formatFigure(f)))

      var format_csv=[(f)=>f,
                       (f)=>f]
      Object.keys(communes[0].csp).filter((key)=>key != "csp8").map((key) => format_csv.push((f)=>f))

      var align=["l", "l"]
      Object.keys(communes[0].csp).filter((key)=>key != "csp8").map((key) => align.push("r"))

      var rows = cols_to_rows(cols)
      var name_csv = "profil_csp"

      var sources_table = ["dossier_complet"]
    }

    return {selected, headlines, rows, align, format_table, format_csv, name_csv, sources_table}
  }

  constructor(props) {
    super(props);
    let selected_init = "motorisation_rate"

    this.state = Object.assign({}, {
      viewMap: true,
      viewTable: false,
    },
    this.getCommunesMap(selected_init),
    this.getCommunesTable(selected_init));
  }

  setView = (view) => {
      this.setState({
        viewMap: view=="map",
        viewTable: view=="table",
      })
  }
  displayCategory = (selected) => {
    this.setState(this.getCommunesMap(selected))
    this.setState(this.getCommunesTable(selected))
  }

  componentDidMount() {
    // --- init map
    let mymap = this.mymap = getMyMap("population_profile_map", true, 0.3);
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
    let data_list_age = [{selected: "-18_prop", label: "- part des 17 ans et moins"},
                         {selected: "+65_prop", label: "- part des 65 ans et plus"}]
    let data_list_status = [{selected: "employed_prop", label: "- actifs & actives"},
                            {selected: "retired_prop", label: "- à la retraite"},
                            {selected: "scholars_inf_prop", label: "- scolaires (jusqu'à 17 ans)"},
                            {selected: "scholars_sup_prop", label: "- scolaires (18 ans et plus)"},
                            {selected: "unemployed_prop", label: "- au chômage"}]

    let communes = this.props.territory.communes;
    let data_list_csp = [];
    Object.keys(communes[0].csp).filter((key)=> key != "csp8" && key != "total15+").
    map((key) => data_list_csp.push({selected: key, label: "- " + communes[0].csp[key]["label"].toLowerCase()}))

    return(
          <div className="row content mt-5 mb-5">

            <div className="col-3">
                <div className="row">
                  <div className="col-12">
                    <h3 className="mb-3">profil de la population</h3>
                  </div>
                </div>

                <div className="row">
                  <div className="col-12 line-border">
                      <DataSelectionButton selected={this.state.selected === "motorisation_rate"}
                                           display_category={this.displayCategory.bind(this, "motorisation_rate")} label="taux de motorisation des ménages" />

                    <p className="mb-2 mt-4"><i>répartition par âge :</i></p>
                      {data_list_age.map((d)=>
                        <DataSelectionButton selected={this.state.selected === d.selected}
                                             display_category={this.displayCategory.bind(this, d.selected)} label={d.label} />
                      )}

                    <p className="mb-2 mt-4"><i>répartition par statut :</i></p>
                      {data_list_status.map((d)=>
                        <DataSelectionButton selected={this.state.selected === d.selected}
                                             display_category={this.displayCategory.bind(this, d.selected)} label={d.label} />
                      )}

                    <p className="mb-2 mt-4"><i>répartition par CSP des +15 ans :</i></p>
                      {data_list_csp.map((d)=>
                        <DataSelectionButton selected={this.state.selected === d.selected}
                                             display_category={this.displayCategory.bind(this, d.selected)} label={d.label} />
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
                                    id="population_profile_map"
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
                <DownloadButton download={downloadCSV.bind(this, this.state.headlines, this.state.rows, this.state.format_csv, this.state.name_csv)} label="Télécharger le tableau au format CSV"/>
              </div>

          </div>
        </div>
    )
  }
}

export default PopulationProfile;
