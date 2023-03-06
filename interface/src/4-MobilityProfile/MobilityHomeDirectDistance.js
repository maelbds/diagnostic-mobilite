import React, { Component } from 'react';

import {c_modes, c_direct_indirect} from '../a-Graphic/Colors';

import {formatFigure} from '../f-Utilities/util_func';

import PlotBar from '../c-PlotlyFigures/PlotBar';
import SourcesRow from '../f-Utilities/SourcesRow'

class MobilityHomeDirectDistance extends React.Component {
  constructor(props) {
   super(props);

   this.state = {
     unit: "number",
     label: "nombre de déplacements"
   };
 }

 setUnit = (unit, label) => {
     this.setState({
       unit: unit,
       label: label
     })
 }

  render() {
    function set_label(array){
      return array.map((l)=>"<span style='font-weight: 300;'>" + l + "</span>")
    }

    let distance_class_order = ["moins de 1 km", "entre 1 et 5 km", "entre 5 et 7 km",
    "entre 7 et 10 km", "entre 10 et 20 km", "plus de 20km", "autre/imprécis"]


    var unit = this.state.unit

    var territory = this.props.territory;

    let home_trvls_by_dist = territory.travels_analysis["4_focus"].home.by_distance_class;

    let labels = set_label(Object.keys(home_trvls_by_dist[unit]))

    let total = Object.values(home_trvls_by_dist[unit]).reduce((a,b) => a + b);

    let values = {
      "total": Object.values(home_trvls_by_dist[unit]).map((l)=>l/total*100),
    }
    let texts = {
      "total": values["total"].map((v)=>formatFigure(v, 2) + "%"),
    }
    let hovertexts = {
      "total": values["total"].map((v)=>formatFigure(v, 2) + "%"),
    }

    return(

      <div className="row mt-5">
        <div className="col-12">

          <div className="row">
            <div className="col-auto">
              <h4 className="mb-2">répartition par classes de distances</h4>
            </div>
          </div>

          <div className="row mt-1 mb-1">
            <div className="col-auto pr-1">
              <p onClick={this.setUnit.bind(this, "distance", "distance parcourue")}
                 className={this.state.unit == "distance" ? "button p-1 pl-2 pr-2 active" : "button p-1 pl-2 pr-2"}>Distance parcourue</p>
            </div>
            <div className="col-auto pr-1">
              <p onClick={this.setUnit.bind(this, "number", "nombre de déplacements")}
                 className={this.state.unit == "number" ? "button p-1 pl-2 pr-2 active" : "button p-1 pl-2 pr-2"}>Nombre de déplacements</p>
            </div>
            <div className="col-auto pr-1">
              <p onClick={this.setUnit.bind(this, "ghg_emissions", "émissions de GES")}
                 className={this.state.unit == "ghg_emissions" ? "button p-1 pl-2 pr-2 active" : "button p-1 pl-2 pr-2"}>Emissions de GES</p>
            </div>
          </div>

          <div className="row">
            <div className="col-12">
                      <PlotBar values={values}
                               labels={labels}
                               texts={texts}
                               hovertexts={hovertexts}
                               colors={c_direct_indirect}
                               order={set_label(distance_class_order)}
                               id="home_direct_distance"
                               height="350"/>
            </div>
          </div>


          <div className="row mt-1"></div>
          {Object.keys(territory.sources).includes("emd") ?
            <SourcesRow sources={territory.sources}
                   concerned={["emd"]}/> :
             <SourcesRow sources={territory.sources}
                    concerned={["entd", "census", "mobpro", "bpe"]} processed={true}/>}

      </div>
    </div>

    )
  }
}

export default MobilityHomeDirectDistance;
