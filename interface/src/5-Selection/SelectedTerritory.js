import React, { Component } from 'react';
import * as d3 from "d3";
import proj4 from "proj4";
import proj4d3 from "proj4d3";
import booleanPointInPolygon from "@turf/boolean-point-in-polygon";
import * as topojson from "topojson";

import {c_light, c_green_text as c_green, c_green_text_t, c_violet} from "../a-Graphic/Colors"

const L = window.L;

class SelectedTerritory extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      title: ""
    };
  }

  updateTitle = (title) => {
    this.setState({
      title: title
    });
  }

  componentDidUpdate(prevProps, prevState){
    if(prevProps.selected_communes != this.props.selected_communes){
      const mostFrequent = arr =>
        Object.entries(
          arr.reduce((a, v) => {
            a[v] = a[v] ? a[v] + 1 : 1;
            return a;
          }, {})
        ).reduce((a, v) => (v[1] >= a[1] ? v : a), [null, 0])[0];

      let communes_by_zone = new Map([1, 2, 3].map((z)=>[z, this.props.selected_communes.filter((g, i) => this.props.selected_zones[i] == z)]))
      let epcis = this.props.selected_communes.map((c)=> this.props.communes["code_epci"][c])
      let main_epci = mostFrequent(epcis)
      let main_epci_name = this.props.epci[main_epci]
      if (main_epci_name == undefined) main_epci_name = "Sans titre"
      console.log(main_epci_name)
      this.setState({title: main_epci_name})
    }
  }

  render() {
    let communes_by_zone = new Map([1, 2, 3].map((z)=>[z, this.props.selected_communes.filter((g, i) => this.props.selected_zones[i] == z)]))

    return(
    <div>
      <div className="row mb-5">
        <div className="col-4">
          <h2 className="bottom-line-green">validation du territoire</h2>
        </div>
        <div className="col-8">
          <p className="mb-2">Le territoire d'étude sélectionné comprend <span className="highlight-green">{this.props.selected_communes.length} communes</span>, selon la répartition par zones ci-dessous.</p>
          <p>Indiquer un nom à ce territoire pour le sauvegarder et le retrouver lors d'une prochaine session.</p>
        </div>
      </div>

      <div className="row mb-5">
          <div className="col-8">
             <div className="row m-0 pt-2 pb-2"  style={{border: "3.5px solid var(--green-t)"}}>
                 {[1, 2, 3].map((z)=>
                   <div className="col-4">
                     <p><b>Zone {z} </b></p>
                     <p className="mb-2"><i>({communes_by_zone.get(z).length} {communes_by_zone.get(z).length == 1 ? "commune" : "communes"})</i></p>
                     <div style={{height: "250px", overflow: "auto"}}>
                       {communes_by_zone.get(z).sort((a, b)=> this.props.d_communes.get(a) > this.props.d_communes.get(b)  ? 1 : -1)
                                               .map((g) => <p className="table-line pt-1 pb-1">{this.props.d_communes.get(g)} <i>({g})</i></p>)}
                     </div>
                   </div>
                 )}
             </div>
          </div>

          <div className="col-4">
            <div className="row">
              <div className="col-12">
                    <p className="mr-1">Nom de votre territoire d'étude :</p>
               </div>
            </div>

            <div className="row mb-5">
               <div className="col-12">
                     <input type="text" className="input-text" id="title" value={this.state.title}
                            onChange={(e) => this.updateTitle(e.target.value)}></input>
                </div>
             </div>

             <div className="row m-0">
               <div className="col-auto p-2 pr-3" style={{backgroundColor: c_green_text_t, cursor: "pointer"}}
                     onClick={this.props.loadTerritory.bind(this,
                                                  this.state.title,
                                                  this.props.selected_communes,
                                                  this.props.selected_zones)}>
                 <p><b>→ Obtenir le diagnostic </b></p>
               </div>
             </div>

          </div>

        </div>

    </div>
    )
  }
}

export default SelectedTerritory;
