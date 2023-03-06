import React, { Component } from 'react';

import getMyMap, {getLegendMode} from '../b-LeafletMap/leaflet_map';
import {createCommuneBordersLayer, getCommunesMassElements} from '../b-LeafletMap/LeafletMapElement/createCommune';
import {createCommunesNamesLayerEasy} from '../b-LeafletMap/LeafletMapElement/createCommuneName';
import {createGridLayer} from '../b-LeafletMap/LeafletMapElement/createGrid';
import {createCyclePath} from '../b-LeafletMap/LeafletMapElement/createCyclePath';
import {createPlacesLayer} from '../b-LeafletMap/LeafletMapElement/createPlaceLayer';
import {createRoutesLayer} from '../b-LeafletMap/LeafletMapElement/createRoute';

import LeafletMapLegend from '../b-LeafletMap/LeafletMapLegend';
import Info from '../f-Utilities/Info';
import Table from '../d-Table/Table';
import SourcesRow from '../f-Utilities/SourcesRow';
import ViewButton from '../f-Utilities/ViewButton';
import DownloadButton from '../f-Utilities/DownloadButton';
import DataSelectionButton from '../f-Utilities/DataSelectionButton';

import {c_missing_data, c_gradient_greens, c_gradient_reds_greens, c_yellow, c_markers, c_public_transport, c_railway} from '../a-Graphic/Colors';
import {p_size_0, p_size_1, p_size_2, p_size_3, r_size_1} from '../a-Graphic/Layout';
import {formatFigure, titleCase} from '../f-Utilities/util_func';


class PublicTransport extends React.Component {
  getCommunesMap(selected_background, selected_modes){
    /* COMMUNES */
    let communes = this.props.territory.communes;
    let communes_coords = communes.map((c) => c.center);
    let communes_names = communes.map((c) => c.name);

    let places = this.props.territory.places;

    // BACKGROUND
    if(selected_background == "borders"){
      let communes_layer = createCommuneBordersLayer(communes)
      var layer_to_fit = communes_layer
      var layers = [communes_layer]
      var sources = []
      var legend = []
    }
    else if(selected_background == "gridded_pop"){
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
    else if(selected_background == "gridded_income"){
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

    // PUBLIC TRANSPORT
    var public_transport = this.props.territory.public_transport;
    public_transport = public_transport.filter((pt)=>!pt.name.toLowerCase().includes("tad -") && !pt.name.toLowerCase().includes("transport à la demande"))

    var public_transport_routes = [];
    var public_transport_labels = [];
    var pt_stops = [];

    for (let pt of public_transport){
        if (pt.type == 0){
          let route = [];
          for (var i=0; i<pt.stops_lat.length; i++){
            route.push([pt.stops_lat[i], pt.stops_lon[i]])
          }
          public_transport_routes.push(route);
          public_transport_labels.push(pt.name);
          pt_stops = pt_stops.concat(pt.stops);
        }
    }

    var stops_coords = pt_stops.map((a) => a.coords)
    var stops_labels = pt_stops.map((a) => a.name)

    var routes_to_coords = (routes) => {
      let all_coords = [];
      for (let r of routes){
        let coords = [];
        for (var i=0; i<r.stops_lat.length; i++){
          coords.push([r.stops_lat[i], r.stops_lon[i]])
        }
        all_coords.push(coords)
      }
      return all_coords
    }
    var routes_to_labels = (routes) => {return routes.map((r)=>r.name)}
    var routes_to_stop_coords = (routes) => {return routes.map((route)=>route.stops.map((stop)=> stop.coords)).flat(1)}
    var routes_to_stop_names = (routes) => {return routes.map((route)=>route.stops.map((stop)=> stop.name)).flat(1)}


    if(selected_modes.includes("train")){
      let railways = this.props.territory.railways.filter((r)=>r != null);

      let train_stations = places.filter((p) => ["gare de voyageurs d'intérêt local", "gare de voyageurs d'intérêt régional", "gare de voyageurs d'intérêt national"].includes(p.type_fr.toLowerCase()))
      let train_stations_coords = train_stations.map((a) => a.coords)

      let color = c_railway
      let width = r_size_1
      let color_stops = c_markers[1]
      let size_stops = p_size_1

      layers.push(createRoutesLayer(railways, null, width, [color]))
      layers.push(createPlacesLayer(train_stations_coords, size_stops/2, color_stops))

      legend.push({type: "LegendSpace", params: {}})
      legend.push({type: "LegendPlace", params: {label: "Gare", color: color_stops, size: size_stops+2}})
      legend.push({type: "LegendRoute", params: {label: "Voie ferrée", color: color, size: width*2+1}})
      sources.push("osm")
    }

    let colors_routes = c_public_transport
    let color_stops = c_markers[0]
    let width_routes = r_size_1
    let size_stops = p_size_0

    var pt_routes = []

    if(selected_modes.includes("metro")){
      let metro_routes = public_transport.filter((pt)=>pt.type == 1);
      pt_routes = pt_routes.concat(metro_routes)
    }
    if(selected_modes.includes("tram")){
      let tram_routes = public_transport.filter((pt)=>pt.type == 0);
      pt_routes = pt_routes.concat(tram_routes)
    }
    if(selected_modes.includes("bus")){
      let bus_routes = public_transport.filter((pt)=>pt.type == 3);
      pt_routes = pt_routes.concat(bus_routes)
    }
    if(selected_modes.includes("other")){
      let other_routes = public_transport.filter((pt)=>(pt.type != 0) && (pt.type != 1) && (pt.type != 3));
      pt_routes = pt_routes.concat(other_routes)
    }

    if (pt_routes.length>0){
      layers.push(createRoutesLayer(routes_to_coords(pt_routes), routes_to_labels(pt_routes), width_routes, colors_routes))
      layers.push(createPlacesLayer(routes_to_stop_coords(pt_routes), width_routes/2+1.2, color_stops, routes_to_stop_names(pt_routes)))

      legend.push({type: "LegendSpace", params: {}})
      legend.push({type: "LegendPlace", params: {label: "Arrêt de transport en commun", color: color_stops, size: size_stops+2}})
      legend.push({type: "LegendRoute", params: {label: "Ligne de transport en commun", color: colors_routes.slice(0, pt_routes.length), size: width_routes*2+1}})
      sources.push("transportdatagouv")
    }


    layers.push(createCommunesNamesLayerEasy(communes))

    let sources_map = sources.length>1 ? [...new Set(sources)] : sources;
    return {selected_background, selected_modes, layer_to_fit, layers, legend, sources_map}
  }


  constructor(props) {
    super(props);
    let selected_modes_init = ["metro", "bus"]
    let selected_background_init = "borders"

    this.state = Object.assign({}, {
      viewMap: true,
      viewTable: false,
    },
    this.getCommunesMap(selected_background_init, selected_modes_init))
  }

  displayCategory = (selected_background) => {
      this.setState(function(prevState, prevProps){
        return this.getCommunesMap(selected_background, prevState.selected_modes)
      })
  }
  displayMode = (selected_mode) => {
      this.setState(function(prevState, props) {
        let index = prevState.selected_modes.indexOf(selected_mode);
        let new_selected_modes = [];
        if (index > -1) {
          new_selected_modes = prevState.selected_modes
          new_selected_modes.splice(index, 1) // 2nd parameter means remove one item only
        }
        else{
          new_selected_modes = prevState.selected_modes.concat([selected_mode])
        }
        return this.getCommunesMap(prevState.selected_background, new_selected_modes)
      });
  }

  componentDidMount() {
    // --- init map
    let mymap = this.mymap = getMyMap("public_transport", true, 0.3);
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
                     {selected: "gridded_pop", label: "population carroyée"},
                     {selected: "gridded_income", label: "niveau de vie moyen au carreau"}]
    let pt_modes = {
       "metro": "métro",
       "tram": "tramway",
       "bus": "bus",
       "train": "train",
       "autre": "autre"
      }

    return(
          <div className="row content mt-4 mb-5">

            <div className="col-3">
                <div className="row">
                  <div className="col-12">
                    <h3 className="mb-3">transports en commun</h3>
                  </div>
                </div>

                <div className="row">
                  <div className="col-12 line-border">

                    <p className="mb-2"><i>modes :</i></p>
                     {Object.keys(pt_modes).map((mode, i)=>
                       <div className="form-check">
                         <input className="form-check-input ml-0 mt-2" type="checkbox" value={mode} id={"pt" + i}
                         checked={this.state.selected_modes.includes(mode)}
                         onChange={ this.displayMode.bind(this, mode) }  />
                         <label className="form-check-label" for={"pt" + i}>
                           <p>{pt_modes[mode]}</p>
                         </label>
                        </div>
                     )}

                    <p className="mb-2 mt-4"><i>fond de carte :</i></p>
                    {data_list.map((d)=>
                      <DataSelectionButton selected={this.state.selected_background === d.selected}
                                           display_category={this.displayCategory.bind(this, d.selected)} label={d.label} />
                    )}

                  </div>
                </div>

                <div className="row mt-4">
                  <div className="col-12">
                    <p className="mb-1">La population carroyée est la population par carreau de 200m de côté. Le niveau de vie moyen au carreau est de <b>1926€/mois</b> à l'échelle du pays.<Info content="Le niveau de vie moyen au carreau (200m de côté) correspond à la somme des niveaux de vie winsorisés des individus du carreau divisé par le nombre d'individus du carreau. On parle toujours du revenu disponible." /></p>
                  </div>
                </div>
            </div>

            <div className="col-9">
                  <LeafletMapLegend legend={this.state.legend}
                                    all_sources={this.props.territory.sources}
                                    concerned_sources={this.state.sources_map}
                                    id="public_transport"
                                    height="500px"/>
            </div>

        </div>
    )
  }
}

export default PublicTransport;
