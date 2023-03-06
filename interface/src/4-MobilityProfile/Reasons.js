import React from 'react';

import {c_reasons} from '../a-Graphic/Colors';
import PlotBarStacked from '../c-PlotlyFigures/PlotBarStacked'

import {formatFigure} from '../f-Utilities/util_func';

class Reasons extends React.Component {
  render(){

    function sort_reasons(reasons){
      let reasons_order = {}
      Object.keys(c_reasons).map((key, i)=> reasons_order[key] = i)

      function comparison(r1, r2){
        return reasons_order[r2[0]] - reasons_order[r1[0]]
      }
      return reasons.sort(comparison)
    }

    function label_text(array){
      var total = array.map((a)=>a[1]).reduce((a,b) => a + b, 0);
      var text = array.map((a) => "<span style='font-size: 1.5vw;'>" + formatFigure(a[1]/total*100, 2) +
                                      " %</span></br></br><span style='font-weight: 300;'>" + a[0] + "</span>");
      return text
    }

    function colors(reasons){
      return reasons.map((r)=> c_reasons[r[0]])
    }


    let territory = this.props.territory;
    let reasons_number = territory.travels_analysis["1_key_figures"].reasons.number
    reasons_number = Object.keys(reasons_number).map((key)=>[key, reasons_number[key]])
    reasons_number = sort_reasons(reasons_number)
    let reasons_distance = territory.travels_analysis["1_key_figures"].reasons.distance
    reasons_distance = Object.keys(reasons_distance).map((key)=>[key, reasons_distance[key]])
    reasons_distance = sort_reasons(reasons_distance)


    return(
      <div className="row">
        <div className="col">

          <div className="row">
            <div className="col-auto">
              <h3 className="mb-0">motifs</h3>
            </div>
          </div>

          <div className="row">
            <div className="col-6">
              <PlotBarStacked values={reasons_number.map((m)=>m[1])}
                       labels={label_text(reasons_number)}
                       id="all_travels_reasons_2"
                       colors={colors(reasons_number)}
                       height="450"/>
              <p className="text-center mt-3">Répartition par motif en nombre de déplacements</p>
            </div>
            <div className="col-6">
              <PlotBarStacked values={reasons_distance.map((m)=>m[1])}
                       labels={label_text(reasons_distance)}
                       id="all_travels_reasons_distance"
                       colors={colors(reasons_distance)}
                       height="450"/>
              <p className="text-center mt-3">Répartition par motif en km parcourus</p>
            </div>
          </div>

        </div>
      </div>

  );
  }
}

export default Reasons;
