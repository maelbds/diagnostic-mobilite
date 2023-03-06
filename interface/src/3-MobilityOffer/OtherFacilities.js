import React, { Component } from 'react';
import {c_blue as c_irve, c_orange as c_bnlc} from '../a-Graphic/Colors';
import {p_size_1} from '../a-Graphic/Layout';

import getMyMap from '../b-LeafletMap/leaflet_map';
import {createCommuneBordersLayer} from '../b-LeafletMap/LeafletMapElement/createCommune';
import {createCommunesNamesLayerEasy} from '../b-LeafletMap/LeafletMapElement/createCommuneName';
import {createPlacesLayer} from '../b-LeafletMap/LeafletMapElement/createPlaceLayer';

import LegendPlace from '../b-LeafletMap/Legend/LegendPlace';

import SourcesRow from '../f-Utilities/SourcesRow'

class OtherFacilities extends React.Component {

  componentDidMount() {
    /* IRVE */
    let irve = this.props.territory.irve;

    function name_irve(name, nb_pdc, power, date){
      let nb = nb_pdc==null ? "/" : nb_pdc
      let w = power==null ? "/" : power
      return "<b>" + name + " </b></br> " + nb_pdc + " points de charge - " + w + "W </br><span className='small-text'><i>(mis à jour le " + date + ")</i></span>"
    }
    let irve_coords = irve.map((a) => [a.lat, a.lon])
    let irve_labels = irve.map((a) => name_irve(a.nom_station, a.nbre_pdc, a.puissance_nominale, a.date_maj))

    /* BNLC */
    let bnlc = this.props.territory.bnlc;

    function name_bnlc(name, nb_pl, nb_pmr, date){
      let nb1 = nb_pl==null ? "/" : nb_pl
      let nb2 = nb_pmr==null ? "/" : nb_pmr
      return "<b>" + name + " </b></br> " + nb1 + " places de parking dont " + nb2 + " PMR </br><span className='small-text'><i>(mis à jour le " + date + ")</i></span>"
    }
    let bnlc_coords = bnlc.map((a) => [a.lat, a.lon])
    let bnlc_labels = bnlc.map((a) => name_bnlc(a.name, a.nbre_pl, a.nbr_pmr, a.date_maj))

    /* COMMUNES */
    let communes = this.props.territory.communes;
    let communes_coords = communes.map((c) => c.center);
    let communes_names = communes.map((c) => c.name);

    // --- init map
    let mymap = getMyMap(this.props.id, true, 0.3);

    // --- create layers
    let communes_layer = createCommuneBordersLayer(communes)
    let irve_places_layer = createPlacesLayer(irve_coords, p_size_1/2, c_irve, irve_labels);
    let bnlc_places_layer = createPlacesLayer(bnlc_coords, p_size_1/2, c_bnlc, bnlc_labels);
    let names = createCommunesNamesLayerEasy(communes)

    communes_layer.addTo(mymap)
    irve_places_layer.addTo(mymap)
    bnlc_places_layer.addTo(mymap)
    names.addTo(mymap)

    // --- center the map
    mymap.fitBounds(communes_layer.getBounds());
  }


  render() {
    return(
      <div className="row mt-5">
        <div className="col">

          <div className="row">
            <div className="col-12">
              <h3 className="mb-3">autres infrastructures</h3>
            </div>
          </div>

          <div className="row align-items-end">
            <div className="col-10">
              <div style={{height: "600px"}} id={this.props.id}></div>
            </div>
            <div className="col-2 pl-0 pr-0">
                <LegendPlace label="Borne de recharge électrique" color={c_irve} size={p_size_1+2}/>
                <div className="mt-2 mb-2"></div>
                <LegendPlace label="Lieu de covoiturage" color={c_bnlc} size={p_size_1+2}/>
            </div>
          </div>

         <SourcesRow sources={this.props.territory.sources}
                concerned={["transportdatagouv_irve", "transportdatagouv_bnlc"]}/>

        </div>
      </div>
    )
  }
}

export default OtherFacilities;
