import React, { Component } from 'react';

import getMyMap, {createResidentialAreasMassLayer, createResidentialAreasWhiteZoneLayer} from './leaflet_map';

import LegendResidentialArea from '../b-LeafletMap/Legend/LegendResidentialArea';
import LegendClusterArea from '../b-LeafletMap/Legend/LegendClusterArea';
import LegendValues from '../b-LeafletMap/Legend/LegendValues';
import LegendValuesFlows from '../b-LeafletMap/Legend/LegendValuesFlows';

class LeafletMapCaseStudy extends React.Component {

  componentDidMount() {
    var distance_matrix = this.props.territory.distance_matrix;

    /* COMMUNES */
    var communes = this.props.territory.communes;
    var communes_coords = communes.map((c) => c.center);
    var communes_names = communes.map((c) => c.name);
    var c_population = communes.map((c) => c.population);
    var c_population_retired = communes.map((c) => c.status.retired);
    var c_population_employed = communes.map((c) => c.status.employed);
    var c_population_scholars = communes.map((c) => c.status.scholars_11_14 + c.status.scholars_15_17 + c.status.scholars_18 + c.status.scholars_2_5 + c.status.scholars_6_10);

    var all_communes_coords = communes.concat(this.props.territory.influence_communes.filter((c) => ["NIORT", "CHAURAY", "LA MOTHE ST HERAY", "ROUILLE"].includes(c.name))).map((c) => c.center);
    var all_communes_names = communes.concat(this.props.territory.influence_communes.filter((c) => ["NIORT", "CHAURAY", "LA MOTHE ST HERAY", "ROUILLE"].includes(c.name))).map(
      (c) => '<span class="small-text">' + c.name + "</span></br>" + Math.round(c.mass*100) +"%");

    /* AREAS */
    var places = this.props.territory.places
    var areas = this.props.territory.areas
    var areas_coords = areas.map((a) => a.coords)
    var areas_labels = areas.map((a) => '<span class="small-text">' + a.name + "</span></br>" + a.mass)

    var characteristic_food = places.filter((p) => ["supermarché", "hypermarché", "épicerie"].includes(p.type.toLowerCase()))
    var characteristic_food_extended = places.filter((p) => ["boulangerie", "boucherie charcuterie", "poissonnerie", "supérette"].includes(p.type.toLowerCase()))
    var characteristic_shop = places.filter((p) => ["grande surface de bricolage", "droguerie quincaillerie bricolage", "librairie, papeterie, journaux", "magasin de vêtements", "fleuriste-jardinerie-animalerie", "magasin d'optique"].includes(p.type.toLowerCase()))
    var characteristic_services = places.filter((p) => ["banque, caisse d'épargne", "bureau de poste", "agence postale", "relais postal", "coiffure"].includes(p.type.toLowerCase()))
    var characteristic_leisure = places.filter((p) => ["cinéma", "bibliothèque", "restaurant- restauration rapide", "gymnase"].includes(p.type.toLowerCase()))
    var characteristic_health = places.filter((p) => ["médecin généraliste", "pharmacie"].includes(p.type.toLowerCase()))
    var characteristic_education = places.filter((p) => ["école maternelle", "école élémentaire", "collège", "lycée d'enseignement général et/ou technologique", "lycée d'enseignement professionnel"].includes(p.type.toLowerCase()))

    var characteristic_places = places.filter((p) => p.characteristic == 1)

    var activity_cluster = this.props.territory.activity_cluster

    /* PUBLIC TRANSPORT */
    var public_transport = this.props.territory.public_transport;
    var stops_pt = [];
    public_transport.map((pt) => stops_pt = stops_pt.concat(pt.stops));
    var railways = this.props.territory.railways.filter((r)=>r != null);

    var train_stations = places.filter((p) => ["gare de voyageurs d'intérêt local", "gare de voyageurs d'intérêt régional", "gare de voyageurs d'intérêt national"].includes(p.type.toLowerCase()))

    /* RESIDENTIAL */
    var residential_areas = [];
    this.props.territory.communes.map((c) => residential_areas = residential_areas.concat(c.residential_areas));
    var ra_population = residential_areas.map((ra) => ra.population)


    /* MOBILITY */
    var destinations = this.props.territory.all_travels.destinations
    destinations = destinations.filter((d)=>d.mass>0.01)
    var destinations_coords = destinations.map((c) => c.center);
    var destinations_labels = destinations.map((c) => '<span class="small-text">' + c.name + "</span></br>" + Math.round(c.mass*100) +"%");

    var all_travels_flows = this.props.territory.all_travels_flows;



    // --- init map
    var mymap = this.mymap = getMyMap(this.props.id, true, 0.2);
    const flows_info = document.getElementById("flows_info");

    // --- create layers
    //var communes_layer = this.communes_layer = createCommunePopulationLayer(mymap, communes, c_population);
    //var residential_areas_layer = this.residential_areas_layer = createResidentialAreasMassLayer(mymap, residential_areas, ra_population);
    //var residential_areas_layer = this.residential_areas_layer = createResidentialAreasWhiteZoneLayer(mymap, residential_areas, areas_to_map, distance_matrix);
    //var pt_routes_layer = this.pt_routes_layer = createPTRoutesLayer(mymap, public_transport);
    //var railways_layer = this.railways_layer = createRailwaysLayer(mymap, railways);
    //var flows_layer = this.flows_layer = createFlowsLayer(mymap, all_travels_flows, flows_info);
    //var areas_layer2 = this.areas_layer2 = createAreasLayer(mymap, characteristic_places, null, null, "red");
    //var areas_layer = this.areas_layer = createAreasLayer(mymap, areas_to_map);

    // --- center the map
    //mymap.fitBounds(names_layer.getBounds());
  }


  render() {
    var communes = this.props.territory.communes;
    return(
      <div className="row align-items-end">
        <div className="col-2">
              <div className="row">
                <div className="col" id="flows_info">
                <p>Passer la souris sur les flux et lieux pour des informations spécifiques.</p>
                </div>
              </div>
             <LegendResidentialArea grey={true}/>
             <LegendClusterArea grey={true}/>
        </div>
        <div className="col-10">
          <div style={{height: "700px"}} id={this.props.id}></div>
        </div>
      </div>
    )
  }
}

export default LeafletMapCaseStudy;
