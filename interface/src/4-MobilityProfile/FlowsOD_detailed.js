import React, { Component } from 'react';
import {c_light, c_background, c_gradient_reds} from '../a-Graphic/Colors';

import getMyMap, {createCommuneBordersLayer, createNamesLayer, createCommuneLayerFlows,
  createCommuneFlowsLayer, getLegendMode, createCommunesNamesLayerEasy} from '../b-LeafletMap/leaflet_map';

import LegendCommune from '../b-LeafletMap/Legend/LegendCommune';
import LegendClusterArea from '../b-LeafletMap/Legend/LegendClusterArea';
import LegendValuesFlows from '../b-LeafletMap/Legend/LegendValuesFlows';
import LegendValues from '../b-LeafletMap/Legend/LegendValues';
import FlowDetailed from './FlowDetailed';

import SourcesRow from '../f-Utilities/SourcesRow';

const L = window.L;

class FlowsOD_detailed extends React.Component {
  constructor(props) {
   super(props);

   this.state = {
     unit: "distance",
     label: "km",
     legend: "de la distance totale",
     limit_flows_nb: 100
   };

 }

  setUnit = (unit, label, legend) => {
      this.setState({
        unit: unit,
        label: label,
        legend: legend
      })
  }
   setNbFlows = (value) => {
       this.setState({
         limit_flows_nb: parseInt(value)
       })
   }


  render() {
    let territory = this.props.territory;
    let flows_od_detailed = territory.travels_analysis["3_flows"].flows_commune_all_detailed;

    let geo_code_dict = territory.geo_code_dict;

    if(geo_code_dict == null){
      geo_code_dict = {}
    }
    let all_communes = territory.communes.concat(territory.influence_communes).concat(territory.work_communes)
    all_communes.map((c)=>geo_code_dict[c.geo_code] = {"center": c.center, "name": c.name})

    return(
      <div className="row content mt-4 mb-5">
        <div className="col-12">

            <div className="row">
              <div className="col-12">
                <h4>Détail des 20 principaux flux entre communes en termes de distance</h4>
              </div>
            </div>

          <div className="row mt-3 mb-3">
            <div className="col-auto pr-1">
              <p onClick={this.setUnit.bind(this, "distance", "km", "de la distance totale")}
                 className={this.state.unit == "distance" ? "button p-1 pl-2 pr-2 active" : "button p-1 pl-2 pr-2"}>Distance parcourue</p>
            </div>
            <div className="col-auto pr-1">
              <p onClick={this.setUnit.bind(this, "number", "déplacements", "du nombre total de déplacements")}
                 className={this.state.unit == "number" ? "button p-1 pl-2 pr-2 active" : "button p-1 pl-2 pr-2"}>Nombre de déplacements</p>
            </div>
            <div className="col-auto pr-1">
              <p onClick={this.setUnit.bind(this, "ghg_emissions", "tCO2eq", "des émissions totales")}
                 className={this.state.unit == "ghg_emissions" ? "button p-1 pl-2 pr-2 active" : "button p-1 pl-2 pr-2"}>Emissions de GES</p>
            </div>
          </div>

          <div className="row align-items-end" style={{height: "400px", overflow: "auto"}}>
            <div className="col-12">

              {flows_od_detailed.map((f) =>
                  <FlowDetailed flow={f} territory={territory} geo_code_dict={geo_code_dict}
                  unit={this.state.unit} label={this.state.label} legend={this.state.legend}
                  significance_threshold={this.props.significance_threshold}/>
              )}

            </div>
          </div>


          <div className="row mt-3 mb-3">
            <div className="col-12">
              <p><u>Note :</u> la précision statistique n'est pas toujours suffisante pour détailler tous les résultats, d'où la mention <i>autre/imprécis</i>.</p>
            </div>
          </div>

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

export default FlowsOD_detailed;
