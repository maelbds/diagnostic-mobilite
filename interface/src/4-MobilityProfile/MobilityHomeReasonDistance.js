import React, { Component } from 'react';

import {c_modes, c_direct_indirect} from '../a-Graphic/Colors';

import {formatFigure} from '../f-Utilities/util_func';

import PlotBar from '../c-PlotlyFigures/PlotBar';
import SourcesRow from '../f-Utilities/SourcesRow'

class MobilityHomeReasonDistance extends React.Component {
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
    var unit = this.state.unit

    var territory = this.props.territory;

    let home_trvls_by_reasons = territory.travels_analysis["4_focus"].home.by_reasons;

    var labels = Object.keys(home_trvls_by_reasons[unit]).filter((l)=> l != "domicile").map((l)=>"<span style='font-weight: 300;'>" + l + "</span>")

    var total_inf7 = Object.values(home_trvls_by_reasons[unit]).filter((v)=> "true" in v).map((v)=>v["true"]).reduce((a,b) => a + b);
    var total_sup7 = Object.values(home_trvls_by_reasons[unit]).filter((v)=> "false" in v).map((v)=>v["false"]).reduce((a,b) => a + b);
    var total = total_inf7 + total_sup7;

    function filter_nan(value){
      if (isNaN(value)){
        return 0
      } else {
        return value
      }
    }

    var values = {
      "Moins de 7km": Object.keys(home_trvls_by_reasons[unit]).filter((l)=> l != "domicile").map((key)=>filter_nan(home_trvls_by_reasons[unit][key]["true"])/total*100),
      "Plus de 7km": Object.keys(home_trvls_by_reasons[unit]).filter((l)=> l != "domicile").map((key)=>filter_nan(home_trvls_by_reasons[unit][key]["false"])/total*100),
      "Total": Object.keys(home_trvls_by_reasons[unit]).filter((l)=> l != "domicile").map((key)=>(filter_nan(home_trvls_by_reasons[unit][key]["false"]) + filter_nan(home_trvls_by_reasons[unit][key]["true"]))/total*100),
    }
    var texts = {
      "Moins de 7km": values["Moins de 7km"].map((v)=>formatFigure(v, 2) + "%"),
      "Plus de 7km": values["Plus de 7km"].map((v)=>formatFigure(v, 2) + "%"),
      "Total": values["Total"].map((v)=>formatFigure(v, 2) + "%"),
    }
    var hovertexts = {
      "Moins de 7km": values["Moins de 7km"].map((v)=>formatFigure(v, 2) + "% - moins de 7km"),
      "Plus de 7km": values["Plus de 7km"].map((v)=>formatFigure(v, 2) + "% - plus de 7km"),
      "Total": values["Total"].map((v)=>formatFigure(v, 2) + "% - total"),
    }

    return(

      <div className="row mt-5">
        <div className="col-12">

          <div className="row">
            <div className="col-auto">
              <h4 className="mb-2">répartition par motif et par distance</h4>
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
                               id="home_reason_distance"
                               height="450"/>
            </div>
          </div>

          <div className="row mt-2">
            <div className="col-12">
              <p><span style={{color: c_direct_indirect[0], fontWeight: 400}}>En jaune, les déplacements de moins de 7km</span>
              ,  <span style={{color: c_direct_indirect[1], fontWeight: 400}}>en rouge, les déplacements de plus de 7km</span>. En gris, le total des deux.</p>
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

export default MobilityHomeReasonDistance;
