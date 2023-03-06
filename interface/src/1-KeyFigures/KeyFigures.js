import React, { Component } from 'react';

import IdentityGeneral from './IdentityGeneral';
import MobilityGeneral from './MobilityGeneral';
import IssuesGeneral from './IssuesGeneral';

import getMyMap from '../b-LeafletMap/leaflet_map';
import {createCommunesLayer} from '../b-LeafletMap/LeafletMapElement/createCommune';
import {createCommunesNamesLayerEasy} from '../b-LeafletMap/LeafletMapElement/createCommuneName';

const L = window.L;


class KeyFigures extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      territory: props.territory
    };
  }

  componentDidMount() {
    var communes = this.props.territory.communes;
    var communes_coords = communes.map((c) => c.center);
    var communes_names = communes.map((c) => c.name + " - " + c.geo_code);

    // --- init map
    var mymap = getMyMap("main_map", false, 0, false, false, false);

    // --- create layers
    var communes_layer = createCommunesLayer(communes, communes_names);
    communes_layer.addTo(mymap)
    var communes_names_layer = createCommunesNamesLayerEasy(communes)
    communes_names_layer.addTo(mymap)

    // --- center the map
    mymap.fitBounds(communes_layer.getBounds());
  }

  render() {
    return(
      <div className="row">
        <div className="col">
          <div className="row">
            <div className="col-6">
              <IdentityGeneral territory={this.state.territory}/>
              {this.state.territory.travels_analysis != null && <MobilityGeneral territory={this.state.territory}/>}
            </div>
            <div className="col-6 d-flex flex-column">
              <div className="row h-100">
                <div className="col">
                    <div style={{height: "100%"}} id="main_map"></div>
                </div>
              </div>
              {this.state.territory.travels_analysis != null && <IssuesGeneral territory={this.state.territory}/>}

            </div>
          </div>
          <div className="row mt-2">
            <div className="col-12">
            </div>
          </div>

        </div>
      </div>
    )
  }
}

export default KeyFigures;
