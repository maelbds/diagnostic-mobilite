import React, { Component } from 'react';
import {c_markers as colors, c_gradient_reds} from '../a-Graphic/Colors';
import {p_size_1, p_size_2, p_size_3, p_size_4} from '../a-Graphic/Layout';

import getMyMap, {createResidentialAreasMassLayer, createResidentialAreasWhiteZoneLayer} from '../b-LeafletMap/leaflet_map';

import LegendResidentialArea from '../b-LeafletMap/Legend/LegendResidentialArea';
import LegendPlace from '../b-LeafletMap/Legend/LegendPlace';
import LegendValues from '../b-LeafletMap/Legend/LegendValues';

class ResidentialAreas extends React.Component {

  componentDidMount() {
    /* Health AREAS */
    var places = this.props.territory.places;
    var places_coords = places.map((c) => c.coords);
    var places_names = places.map((c) => c.name);


    /* COMMUNES */
    var communes = this.props.territory.communes;
    var communes_coords = communes.map((c) => c.center);
    var communes_names = communes.map((c) => c.name);

    /* GRIDDED POPULATION */
    var gridded_population = [].concat(...this.props.territory.communes.map((c)=>c.gridded_population));
    var pop_coords = gridded_population.map((c) => c.coords);
    var pop_masses = gridded_population.map((c) => parseInt(c.population));
    var pop_labels = gridded_population.map((c) => c.population + " - hab");

    /* RESIDENTIAL */
    var residential_areas = [];
    this.props.territory.communes.map((c) => residential_areas = residential_areas.concat(c.residential_areas));
    var ra_population = residential_areas.map((ra) => ra.population)
    var ra_labels = residential_areas.map((ra)=> ra.id + " - " + ra.name + " - " + ra.population + " hab")

    /* CLUSTER */
    var cluster_areas = [];
    this.props.territory.communes.map((c) => cluster_areas = cluster_areas.concat(c.cluster_areas));
    //cluster_areas = cluster_areas.filter((ca)=> ca.category=="education")
    var ca_population = cluster_areas.map((ra) => 10)
    var ca_labels = cluster_areas.map((ra)=> ra.name + " - " + ra.category)

    //var distances = this.props.territory.distance_matrix;

    // --- init map
    var mymap = getMyMap(this.props.id, true, 0.3);

    // --- create layers
    //var communes_layer = createCommuneBordersLayer(mymap, communes)
    createResidentialAreasMassLayer(mymap, cluster_areas, ca_population, ca_labels, "ckmeans", c_gradient_reds);
    //createResidentialAreasWhiteZoneLayer(mymap, residential_areas, doctors_coords, distances);
    //createGriddedLayer(mymap, pop_coords, pop_masses, pop_labels);
    //createResidentialAreasMassLayer(mymap, residential_areas, ra_population, ra_labels, "ckmeans", ["#F6C665"]);
    //createPlacesLayer(mymap, places_coords, p_size_1/2, colors[2], places_names);
    //createCommunesNamesLayerEasy(mymap, communes)

    // --- center the map
    //mymap.fitBounds(communes_layer.getBounds());
  }


  render() {
    var gridded_population = [].concat(...this.props.territory.communes.map((c)=>c.gridded_population));
    var pop_masses = gridded_population.map((c) => parseInt(c.population));

    return(

          <div className="row align-items-end">
            <div className="col-10">
              <div style={{height: "500px"}} id={this.props.id}></div>
            </div>
            <div className="col-2 pl-0 pr-0">
                <p><b>Population du carreau</b></p>
                 <p><i>(carreau de 200m)</i></p>
            </div>
          </div>
    )
  }
}

export default ResidentialAreas;
