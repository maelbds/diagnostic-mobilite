import React, { Component } from 'react';

import getMyMap, {createAreasMassLayer} from '../b-LeafletMap/leaflet_map';
import {createCommunesLayer} from '../b-LeafletMap/LeafletMapElement/createCommune';

import LegendCommune from '../b-LeafletMap/Legend/LegendCommune';
import LegendValue from '../b-LeafletMap/Legend/LegendValue';

import {c_aac as colors} from '../a-Graphic/Colors';

class Organization extends React.Component {

  componentDidMount() {
    /* COMMUNES */
    var communes = this.props.territory.communes;
    var communes_coords = communes.map((c) => c.center);
    var communes_names = communes.map((c) => c.name + " " + c.geo_code);


    // --- init map
    var mymap = this.mymap = getMyMap(this.props.id, true, 0.3);

    var communes_out_influence = communes.filter((c)=>c.aav.type_code_aav == "0")
    var communes_out_influence_label = communes_out_influence.map((c)=>c.aav.type_name_aav)

    var communes_layer = this.communes_layer = createCommunesLayer(communes_out_influence, communes_out_influence_label, colors[0][0]);

    for (let i=1; i<6; i++){
      // ring
      let communes_area_i = communes.filter((c)=>parseInt(c.aav.type_code_aav) == i && parseInt(c.aav.type_code_commune) == "20")
      var communes_area_i_label = communes_area_i.map((c)=>c.aav.type_name_commune + " de " + c.aav.name_aav +"<br/>" + c.aav.type_name_aav)

      let communes_layer_i = createCommunesLayer(communes_area_i, communes_area_i_label, colors[0][i]);
      communes_layer.addLayer(communes_layer_i)

      // pole
      let communes_area_i_p = communes.filter((c)=>parseInt(c.aav.type_code_aav) == i && parseInt(c.aav.type_code_commune) != "20")
      var communes_area_i_p_label = communes_area_i_p.map((c)=>c.aav.type_name_commune + " de " + c.aav.name_aav +"<br/>" + c.aav.type_name_aav)

      let communes_layer_i_p = createCommunesLayer(communes_area_i_p, communes_area_i_p_label, colors[1][i]);
      communes_layer.addLayer(communes_layer_i_p)
    }

    communes_layer.addTo(mymap)

    // --- center the map
    mymap.fitBounds(communes_layer.getBounds());
  }


  render() {
    var communes = this.props.territory.communes;

    var legend=[]

    var communes_out_influence = communes.filter((c)=>c.aav.type_code_aav == "0")
    if(communes_out_influence.length>0){
      legend.push({"value": "Hors attraction des villes", "color": colors[0][0]})
    }
    for (let i=1; i<6; i++){
      // ring
      let communes_area_i = communes.filter((c)=>parseInt(c.aav.type_code_aav) == i && parseInt(c.aav.type_code_commune) == "20")
      if(communes_area_i.length>0){
        legend.push({"value": "Couronne d'une " + communes_area_i[0].aav.type_name_aav.toLowerCase(), "color": colors[0][i]})
      }
      // pole
      let communes_area_i_p = communes.filter((c)=>parseInt(c.aav.type_code_aav) == i && parseInt(c.aav.type_code_commune) != "20")
      if(communes_area_i_p.length>0){
        legend.push({"value": "Pôle d'une " + communes_area_i_p[0].aav.type_name_aav.toLowerCase(), "color": colors[1][i]})
      }
    }


    var intervals = ["Centre", "Première couronne", "Deuxième couronne"]

    return(
      <div className="row content mt-4 mb-5">
        <div className="col-12">

          <div className="row">
            <div className="col-12">
              <h3 className="mb-3">Aires d'attraction des villes</h3>
            </div>
          </div>

          <div className="row align-items-end">
            <div className="col-9">
              <div style={{height: "600px"}} id={this.props.id}></div>
            </div>
            <div className="col-3">
                 <LegendCommune/>
                 {legend.map((l)=>
                    <LegendValue value={l.value} color={l.color}/>
                 )}

            </div>
          </div>

        </div>
      </div>
    )
  }
}

export default Organization;
