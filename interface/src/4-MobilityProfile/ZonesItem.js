import React from 'react';
import {c_zones, c_modes} from '../a-Graphic/Colors';

import getMyMap, {createNamesLayer, createCommunesLayer} from '../b-LeafletMap/leaflet_map';

import PlotPie from '../c-PlotlyFigures/PlotPie'
import ZonesItemExchange from './ZonesItemExchange'

import {formatFigure} from '../f-Utilities/util_func';

class ZonesItem extends React.Component {

    render(){
      var territory = this.props.territory;

      function sort_means(means){
        let means_order = {
          "voiture" : 6,
          "voiture passager": 5,
          "transport en commun": 4,
          "à pied": 3,
          "vélo": 2,
          "moto": 1,
          "autre": 0,
          "other/insignificant": -1,
        };
        function comparison(mean1, mean2){
          return means_order[mean2[0]] - means_order[mean1[0]]
        }
        return means.sort(comparison)
      }

      function sort_value(means_parts_dict){
        let means_parts_list = Object.keys(means_parts_dict).map((key)=>[key, means_parts_dict[key]])
        means_parts_list = sort_means(means_parts_list)
        return means_parts_list.map((mp)=>mp[1])
      }
      function sort_label(means_parts_dict){
        let means_parts_list = Object.keys(means_parts_dict).map((key)=>[key, means_parts_dict[key]])
        means_parts_list = sort_means(means_parts_list)
        let total = Object.values(means_parts_dict).reduce((a,b) => a + b, 0);
        return means_parts_list.map((mp) => "<span style='font-size: 15px;'>" + formatFigure(mp[1]/total*100, 2) +"%</span>")
      }
      function sort_hover(means_parts_dict){
        let means_parts_list = Object.keys(means_parts_dict).map((key)=>[key, means_parts_dict[key]])
        means_parts_list = sort_means(means_parts_list)
        let total = Object.values(means_parts_dict).reduce((a,b) => a + b, 0);
        return means_parts_list.map((mp) => mp[0] + "</br></br><span style='font-weight: 300;'>" + formatFigure(mp[1]/total*100, 2) +"%</span>")
      }
      function sort_color(means_parts_dict){
        let means_parts_list = Object.keys(means_parts_dict).map((key)=>[key, means_parts_dict[key]])
        means_parts_list = sort_means(means_parts_list)
        return means_parts_list.map((mp)=>c_modes[mp[0]])
      }

      function compute_prop(values, concerned_value, unit){
        return values[concerned_value]/territory.travels_analysis["1_key_figures"].total[unit]*100
      }

      var zm = territory.travels_analysis["2_zones"].zones_modes;
      var zmg = territory.travels_analysis["2_zones"].zones_modes_global;
      var zones = Object.keys(zm);
      var zones_nb = Math.max(...zones.map((z)=>parseFloat(z)));

      var m = this.props.main_zone;
      var name_zone = this.props.main_zone > 0 ? "zone " + this.props.main_zone : "extérieur"
      var color_zone = this.props.main_zone > 0 ? this.props.main_zone : 0

      var c_zones_t = c_zones.map((c)=>c+"bf")

      let prop_zone = compute_prop(zmg[this.props.unit],"zones_"+m+"_"+m, this.props.unit)

      return(
        <div className="row pl-1 pr-1">
          <div className="col-12">
              <div className="row mb-4">
                <div className="col-12 pt-2 pb-2" style={{backgroundColor: c_zones_t[color_zone], borderRadius:"3px"}}>
                  <div className="row">
                    <div className="col-12">
                      <h4>{name_zone}</h4>
                    </div>
                  </div>
                  <div className="row align-items-end">
                    <div className="col-3">
                     <p style={{fontSize: "1.5vw", fontWeight: "600"}}>{(prop_zone != undefined) && !isNaN(prop_zone) && zmg["id"]["zones_"+m+"_"+m] > this.props.significance_threshold && formatFigure(prop_zone, 2) + "%"}</p>
                    </div>
                    <div className="col-8">
                        <PlotPie values={sort_value(zm[m][m][this.props.unit])}
                                 labels={sort_label(zm[m][m][this.props.unit])}
                                 text={sort_hover(zm[m][m][this.props.unit], this.props.label)}
                                 colors={sort_color(zm[m][m][this.props.unit])}
                                 id={"zones_means_" + m}
                                 textposition="inside"
                                 height="180"/>
                   </div>
                 </div>
                   <div className="row">
                     <div className="col-12">
                      <p>{zmg[this.props.unit]["zones_"+m+"_"+m] != undefined ?
                      (zmg["id"]["zones_"+m+"_"+m] > this.props.significance_threshold ?
                      formatFigure(zmg[this.props.unit]["zones_"+m+"_"+m], 3) : "/") :
                      "/"} {this.props.label}</p>
                    </div>
                  </div>

                </div>
              </div>

              {/*this.props.main_zone != -1 &&
              <div className="row">
                <div className="col-12">
                  {[...Array(this.props.zones_nb + 1).keys()].slice(this.props.main_zone + 1,).map((to)=>
                    <ZonesItemExchange territory={territory} unit={this.props.unit} zone_from={m} zone_to={to} label={this.props.label}/>
                  )}
                    <ZonesItemExchange territory={territory} unit={this.props.unit} zone_from={m} zone_to={-1} label={this.props.label}/>
                </div>
              </div>
              */}
          </div>
        </div>
    );
  }
}

export default ZonesItem;
