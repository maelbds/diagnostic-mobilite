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

class Incomes extends React.Component {
  getCommunesMap(selected){
    /* COMMUNES */
    let communes = this.props.territory.communes;
    let communes_coords = communes.map((c) => c.center);
    let communes_names = communes.map((c) => c.name);

    if(selected == "median_income"){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "revenues_median",
        legend_label: "Niveau de vie médian",
        legend_unit: "(€/uc/mois)",
        colors: c_gradient_reds_greens.slice(2, 8),
        sources: ["incomes"],
        indicatorFunction: (c) => c.median_income,
        massFunction: (c) => Math.round(c.median_income/12),
        labelFunction: (c) => c.name + " - " + formatFigure(c.median_income/12, 4) + " €/mois/uc</br>",
      })
    }
    else if(selected == "gini"){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "gini",
        legend_label: "Indice de Gini",
        legend_unit: "",
        colors: c_gradient_reds_greens.slice(2, 8).slice().reverse(), // double slice to make a copy
        sources: ["incomes"],
        indicatorFunction: (c) => c.gini,
        massFunction: (c) => c.gini,
        labelFunction: (c) => c.name + " - " + formatFigure(c.gini, 2, false),
      })
    }
    else if(selected == "decile_ratio"){
      var {layer_to_fit, layers, legend, sources} = getCommunesMassElements(communes, {
        mode: "d1/9",
        legend_label: "Écart interdécile",
        legend_unit: "",
        colors: c_gradient_reds_greens.slice(2, 8).slice().reverse(), // double slice to make a copy
        sources: ["incomes"],
        indicatorFunction: (c) => c.decile_ratio,
        massFunction: (c) => c.decile_ratio,
        labelFunction: (c) => c.name + " - " + formatFigure(c.decile_ratio, 2, false),
      })
    }
    else if(selected == "gridded_income"){
      let gridded_population = [].concat(...communes.map((c)=>c.gridded_population));
      let pop_coords = gridded_population.map((c) => c.coords);
      let pop_hh_inc_masses = gridded_population.map((c) => Math.round(c.sum_incomes/c.population/12));
      let pop_hh_inc_labels = gridded_population.map((c) => formatFigure(Math.round(c.sum_incomes/c.population/12)) + " €/mois/hab");

      var legend_values = pop_hh_inc_masses
      var missing_data = false

      let mode = "revenues_mean"
      let legend_label = "Niveau de vie moyen"
      let legend_unit = "(€/uc/mois)"
      let colors = c_gradient_reds_greens.slice(2, 8)

      var sources = ["gridded_pop"]

      let communes_layer = createCommuneBordersLayer(communes);
      let gridded_incomes_layer = createGridLayer(pop_coords, pop_hh_inc_masses, pop_hh_inc_labels, mode, colors);

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

    let headlines=["Code Insee", "Commune", "Niveau de vie médian (€/uc/mois)", "Indice de Gini", "Écart interdécile"]
    let cols=[communes.map((c)=> c.geo_code),
              communes.map((c)=> c.name),
              communes.map((c)=> c.median_income != null ? c.median_income/12 : null),
              communes.map((c)=> c.gini != null ? c.gini : null),
              communes.map((c)=> c.decile_ratio != null ? c.decile_ratio : null)]
    let format_table=[(f)=>f,
                (f)=>f,
                (f)=>formatFigure(f,4),
                (f)=>formatFigure(f,2, false),
                (f)=>formatFigure(f,2, false)]
    let format_csv=[(f)=>f,
                (f)=>f,
                (f)=>Math.round(f),
                (f)=>formatFigure(f,2, false),
                (f)=>formatFigure(f,2, false)]
    let align=["l", "l", "r", "r", "r"]

    let rows = cols_to_rows(cols)
    let sources_table = ["incomes"]
    let name_csv= "revenus_inegalites"
    return {headlines, rows, align, format_table, format_csv, sources_table, name_csv}
  }


  constructor(props) {
    super(props);
    let selected_init = "median_income"

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
    let mymap = this.mymap = getMyMap("incomes", true, 0.3);
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
    let data_list = [{selected: "median_income", label: "niveau de vie médian"},
                     {selected: "gridded_income", label: "niveau de vie moyen au carreau"},
                     {selected: "gini", label: "indice de Gini"},
                     {selected: "decile_ratio", label: "écart interdécile"}]

    return(
          <div className="row content mt-4 mb-5">

            <div className="col-3">
                <div className="row">
                  <div className="col-12">
                    <h3 className="mb-3">revenus et inégalités</h3>
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
                    <p className="mb-1">Le niveau de vie médian est de <b>1828€/mois en France</b>.<Info content="Le niveau de vie est égal au revenu disponible du ménage divisé par le nombre d'unités de consommation (uc). Il est ici calculé sur le revenu disponible qui correspond aux revenus auxquels il faut ajouter les prestations sociales et retirer les impôts directs." />
                    Le niveau de vie moyen au carreau est quant à lui de <b>1926€/mois</b> à l'échelle du pays.<Info content="Le niveau de vie moyen au carreau (200m de côté) correspond à la somme des niveaux de vie winsorisés des individus du carreau divisé par le nombre d'individus du carreau. On parle toujours du revenu disponible." /></p>
                    <p className="mb-1">L'indice de Gini reflète les inégalités globales. A l'échelle nationale il est de <b>0,29</b>.
                      <Info content={"Cet indice est issu de la courbe de Lorenz qui relie les pourcentages de revenus cumulés aux pourcentages de population. Une égalité parfaite indique une droite à 45°," +
                                      "une inégalité totale une droite à zéro avec un pic de revenus dans les derniers déciles de population. L’indice de Gini est le rapport de l’aire résiduelle entre la courbe " +
                                      "des revenus et l’égalité parfaite divisée par l’aire sous la droite à 45°. Ainsi plus il est proche de 1, plus nous sommes dans une société inégalitaire et plus il est proche" +
                                      " de zéro, plus nous sommes dans une société égalitaire. L’indice de Gini traduit une inégalité globale, le rapport interdécile une inégalité ponctuelle"} />
                    L'écart interdécile est de <b>3,4</b> en France.<Info content="L'écart interdécile est le rapport entre le revenu des 10% les plus riches et celui des 10% les plus pauvres. Il traduit les inégalités ponctuelles." /></p>
                  </div>
                </div>
            </div>

            <div className="col-9">
              <div className="row">
                <div className="col-12" style={{display: this.state.viewMap ? "block" : "none"}}>
                  <LeafletMapLegend legend={this.state.legend}
                                    all_sources={this.props.territory.sources}
                                    concerned_sources={this.state.sources_map}
                                    id="incomes"
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

export default Incomes;
