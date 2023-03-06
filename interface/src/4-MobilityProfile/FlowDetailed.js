import React from 'react';
import {c_zones, c_modes, c_reasons, c_light} from '../a-Graphic/Colors';

import getMyMap, {createNamesLayer, createCommunesLayer} from '../b-LeafletMap/leaflet_map';

import ZonesItemExchange from './ZonesItemExchange'
import PlotBarStackedHorizontal from '../c-PlotlyFigures/PlotBarStackedHorizontal';

import {formatFigure} from '../f-Utilities/util_func';

class FlowDetailed extends React.Component {

    render(){
      let significance_threshold = this.props.significance_threshold;

      let territory = this.props.territory;
      let geo_code_dict = this.props.geo_code_dict;

      let flow = this.props.flow;
      let f_modes = flow.total_modes;
      let f_modes_w = flow.total_modes_reason.work;
      let f_modes_o = flow.total_modes_reason.other;
      let unit = this.props.unit;
      let label = this.props.label;

      console.log(geo_code_dict[flow.geocode1]["name"] + " - " + geo_code_dict[flow.geocode2]["name"])
      console.log(flow.total_modes)

      function sort_modes(means){
        let means_order = {
          "voiture" : 6,
          "voiture passager": 5,
          "transport en commun": 4,
          "à pied": 3,
          "vélo": 2,
          "moto": 1,
          "autre": 0,
          "autre/imprécis": -1,
        };
        function comparison(mean1, mean2){
          return means_order[mean2[0]] - means_order[mean1[0]]
        }
        return means.sort(comparison)
      }
      function label_text(means){
        var total = means.map((m)=>m[1]).reduce((a,b) => a + b);
        var text = means.map(
                      (m) => "<span style='font-size: 1.5vw;'>" + formatFigure(m[1]/total*100, 2) +
                                        " %</span></br></br><span style='font-weight: 300;'>" + m[0] + "</span>"
                    );
        return text
      }
      function colors(means){
        return means.map((m)=> c_modes[m[0]])
      }

      const c_r = {
        "lié au travail": c_reasons["travail ↔ autre"],
        "autre": c_reasons["autre"],
        "autre/imprécis": c_light,
      }
      function colors_reasons(reasons){
        return reasons.map((m)=> c_r[m[0]])
      }


      let pb_f_modes = Object.keys(f_modes).filter((m)=> f_modes[m]["id"] >= significance_threshold).map((m)=> [m, f_modes[m][unit]])
      let unknown_part_modes = flow.total[unit] - pb_f_modes.map((m)=>m[1]).reduce((a,b) => a + b, 0)
      pb_f_modes = sort_modes(pb_f_modes)


      let pb_f_modes_reason = []

      for (let m of pb_f_modes){
        let pb_f_mode_reason = []
        let mode_name = m[0]
        let mode_value = m[1]
        Object.keys(f_modes_w).filter((m)=> (f_modes_w[m]["id"] >= significance_threshold) & (m == mode_name)).map((m)=> pb_f_mode_reason.push(["lié au travail", f_modes_w[m][unit]]))
        Object.keys(f_modes_o).filter((m)=> (f_modes_o[m]["id"] >= significance_threshold) & (m == mode_name)).map((m)=> pb_f_mode_reason.push(["autre", f_modes_o[m][unit]]))
        pb_f_modes_reason.push(pb_f_mode_reason)
      }
      pb_f_modes.map((m, i) => pb_f_modes_reason[i].push(["autre/imprécis", m[1] - pb_f_modes_reason[i].map((m)=>m[1]).reduce((a,b) => a + b, 0)]))

      pb_f_modes.push(["autre/imprécis", unknown_part_modes])
      pb_f_modes_reason.push([["autre/imprécis", unknown_part_modes]])
      console.log(pb_f_modes_reason)
      pb_f_modes_reason = pb_f_modes_reason.flat(1)
      console.log(pb_f_modes_reason)

      return(
        <div className="row mb-4">
          <div className="col-3">
            <p>{geo_code_dict[flow.geocode1]["name"]} ↔ {geo_code_dict[flow.geocode2]["name"]}</p>
            <p style={{fontSize: "1.5vw", fontWeight: 600}}>{formatFigure(flow.total[unit], 3)} {label}</p>
          </div>
          <div className="col-9">
            <div className="row">
              <div className="col-2">
                <p>par mode :</p>
              </div>
              <div className="col-10">
                <PlotBarStackedHorizontal values={pb_f_modes.map((m)=>m[1])}
                         labels={label_text(pb_f_modes)}
                         id={"od_detailed_mode_"+flow.geocode1+flow.geocode2}
                         colors={colors(pb_f_modes)}
                         height="57"/>
              </div>
            </div>
            <div className="row mt-1">
              <div className="col-2">
                <p>et selon motif :</p>
              </div>
              <div className="col-10">
                <PlotBarStackedHorizontal values={pb_f_modes_reason.map((m)=>m[1])}
                         labels={label_text(pb_f_modes_reason)}
                         id={"od_detailed_mode_reason_"+flow.geocode1+flow.geocode2}
                         colors={colors_reasons(pb_f_modes_reason)}
                         height="57"/>
              </div>
            </div>
          </div>
        </div>
    );
  }
}

export default FlowDetailed;
