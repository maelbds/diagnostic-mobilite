import React, { Component } from 'react';

import {c_modes, c_direct_indirect} from '../a-Graphic/Colors';
import {formatFigure} from '../f-Utilities/util_func';

import PlotBar from '../c-PlotlyFigures/PlotBar';
import SourcesRow from '../f-Utilities/SourcesRow'

class MobilityWorkDirectDistance extends React.Component {
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

    let by_distance_class = territory.travels_analysis["4_focus"].work.by_distance_class;
    var labels = set_label(Object.keys(by_distance_class[unit]))

    /*
    var total_direct = Object.values(direct_distance[unit]).map((v)=>v["direct"]).reduce((a,b) => a + b);
    var total_indirect = Object.values(direct_distance[unit]).map((v)=>v["indirect"]).reduce((a,b) => a + b);
    var total = total_direct + total_indirect;*/
    let total = Object.values(by_distance_class[unit]).map((d)=>d["direct"]).reduce((a,b) => a + b);

    var values = {
      //"direct": Object.values(direct_distance[unit]).map((v)=>Math.round(v["direct"]/total*1000)/10),
      //"indirect": Object.values(direct_distance[unit]).map((v)=>Math.round(v["indirect"]/total*1000)/10),
      //"total": Object.values(direct_distance[unit]).map((v)=>Math.round((v["indirect"] + v["direct"])/total*1000)/10),
        "total": Object.values(by_distance_class[unit]).map((l)=>l["direct"]/total*100),
    }
    var texts = {
      //"direct": values["direct"].map((v)=>v + "%"),
      //"indirect": values["indirect"].map((v)=>v + "%"),
      //"total": values["total"].map((v)=>v + "%"),
        "total": values["total"].map((v)=>formatFigure(v, 2) + "%"),
    }
    var hovertexts = {
      //"direct": values["direct"].map((v)=>v + "% - non chaîné"),
      //"indirect": values["indirect"].map((v)=>v + "% - chaîné"),
      //"total": values["total"].map((v)=>v + "% - chaîné & non chaîné"),
        "total": values["total"].map((v)=>formatFigure(v, 2) + "%"),
    }

    return(

      <div className="row mt-5">
        <div className="col-12">

          <div className="row">
            <div className="col-auto">
              <h4 className="mb-2">répartition par classes de distances</h4> {/* des trajets non chaînés et chaînés</h4>*/}
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
                               id="work_direct_distance"
                               height="350"/>
            </div>
          </div>

          <div className="row mt-1"></div>
          {Object.keys(territory.sources).includes("emd") ?
            <SourcesRow sources={territory.sources}
                   concerned={["emd"]}/> :
             <SourcesRow sources={territory.sources}
                    concerned={["entd", "census", "mobpro", "bpe"]} processed={true}/>}
          {/*
          <div className="row mt-3">
            <div className="col-12">
              <p>En {this.state.label}, on compte {Math.round(total_direct/total*100)}%
              de <span style={{color: c_direct_indirect[0], fontWeight: 400}}>trajets non chaînés</span> et {100 - Math.round(total_direct/total*100)}% de <span style={{color: c_direct_indirect[1], fontWeight: 400}}>trajets chaînés</span>.</p>
            </div>
          </div>
          */}
      </div>
    </div>

    )
  }
}

export default MobilityWorkDirectDistance;
