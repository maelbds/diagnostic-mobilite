import React from 'react';
import {c_zones, c_modes} from '../a-Graphic/Colors';

import getMyMap, {createNamesLayer, createCommunesLayer} from '../b-LeafletMap/leaflet_map';

import PlotPie from '../c-PlotlyFigures/PlotPie'

import {formatFigure} from '../f-Utilities/util_func';

class ZonesItemExchange extends React.Component {

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

      function filter_domicile(data){
        return Object.assign({}, ...Object.entries(data).filter(([k,v]) => k != "domicile").map(([k,v]) => ({[k]:v})));
      }

      function compute_prop(values, concerned_value, unit){
        return values[concerned_value]/territory.travels_analysis["1_key_figures"].total[unit]*100
      }

      var zm = territory.travels_analysis["2_zones"].zones_modes;
      var zmg = territory.travels_analysis["2_zones"].zones_modes_global;
      var zones = Object.keys(zm);
      var zones_nb = Math.max(...zones.map((z)=>parseFloat(z)));

      var id_from = this.props.zone_from < this.props.zone_to ? this.props.zone_from : this.props.zone_to
      var id_to = this.props.zone_from > this.props.zone_to ? this.props.zone_from : this.props.zone_to

      var name_from = this.props.zone_from > 0 ? "zone " + this.props.zone_from : "extérieur"
      var name_to = this.props.zone_to > 0 ? "zone " + this.props.zone_to : "extérieur"

      var color_from = this.props.zone_from > 0 ? this.props.zone_from : 0
      var color_to = this.props.zone_to > 0 ? this.props.zone_to : 0

      var c_zones_t = c_zones.map((c)=>c+"bf")

      let prop_zone = compute_prop(zmg[this.props.unit],"zones_"+id_from+"_"+id_to, this.props.unit)

      return(
        <div className="row mb-4 pl-1 pr-1">
          <div className="col-12">
            <div className="row mb-1 justify-content-center align-items-end">
                <div className="col-auto">
                    <PlotPie values={sort_value(zm[id_from][id_to][this.props.unit])}
                             labels={sort_label(zm[id_from][id_to][this.props.unit])}
                             text={sort_hover(zm[id_from][id_to][this.props.unit])}
                             colors={sort_color(zm[id_from][id_to][this.props.unit])}
                             id={"zones_means_" + id_from + id_to + this.props.unit }
                             textposition="inside"
                             height="120"
                             width="120"/>
                </div>
                <div className="col-auto pl-0">
                  <p style={{fontSize: "1.5vw", fontWeight: "600"}}>{(prop_zone != undefined) && !isNaN(prop_zone) && zmg["id"]["zones_"+id_from+"_"+id_to] > this.props.significance_threshold && formatFigure(prop_zone, 2) + "%"}</p>
                  <p>{zmg[this.props.unit]["zones_"+id_from+"_"+id_to] != undefined ?
                      (zmg["id"]["zones_"+id_from+"_"+id_to] > this.props.significance_threshold ?
                      formatFigure(zmg[this.props.unit]["zones_"+id_from+"_"+id_to], 3) : "/") :
                      "/"} {this.props.label}</p>
                </div>
            </div>
            <div className="row align-items-center">
                <div className="col-auto p-1 pl-2 pr-2" style={{backgroundColor: c_zones_t[color_from], borderRadius:"3px"}}>
                  <h4>{name_from}</h4>
                </div>
                <div className="col line-arrow">
                </div>
                <div className="col-auto p-1 pl-2 pr-2" style={{backgroundColor: c_zones_t[color_to], borderRadius:"3px"}}>
                  <h4>{name_to}</h4>
                </div>
            </div>
          </div>
        </div>
    );
  }
}

export default ZonesItemExchange;
