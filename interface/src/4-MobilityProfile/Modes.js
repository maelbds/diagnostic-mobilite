import React from 'react';

import {c_modes} from '../a-Graphic/Colors';
import PlotBarStacked from '../c-PlotlyFigures/PlotBarStacked'

import {formatFigure} from '../f-Utilities/util_func';

class Modes extends React.Component {
  render(){

    function sort_modes(modes){
      let modes_order = {
        "voiture" : 6,
        "voiture passager": 5,
        "transport en commun": 4,
        "à pied": 3,
        "moto": 1,
        "vélo": 2,
        "autre": 0
      };
      function comparison(mean1, mean2){
        return modes_order[mean2[0]] - modes_order[mean1[0]]
      }
      return modes.sort(comparison)
    }

    function label_text(modes){
      var total = modes.map((m)=>m[1]).reduce((a,b) => a + b);
      var text = modes.map(
                    (m) => "<span style='font-size: 1.5vw;'>" +formatFigure(m[1]/total*100, 2) +
                                      " %</span></br></br><span style='font-weight: 300;'>" + m[0] + "</span>"
                  );
      return text
    }

    function colors(modes){
      return modes.map((m)=> c_modes[m[0]])
    }


    let territory = this.props.territory;
    let modes_number = territory.travels_analysis["1_key_figures"].modes.number
    modes_number = Object.keys(modes_number).map((key)=>[key, modes_number[key]])
    modes_number = sort_modes(modes_number)

    let modes_distance = territory.travels_analysis["1_key_figures"].modes.distance
    modes_distance = Object.keys(modes_distance).map((key)=>[key, modes_distance[key]])
    modes_distance = sort_modes(modes_distance)


    return(
      <div className="row">
        <div className="col">

          <div className="row">
            <div className="col-auto">
              <h3 className="mb-0">modes</h3>
            </div>
          </div>

          <div className="row">
            <div className="col-6">
              <PlotBarStacked values={modes_number.map((m)=>m[1])}
                       labels={label_text(modes_number)}
                       id="all_travels_modes_number"
                       colors={colors(modes_number)}
                       height="450"/>
              <p className="text-center mt-3">Répartition modale en nombre de déplacements</p>
            </div>
            <div className="col-6">
              <PlotBarStacked values={modes_distance.map((m)=>m[1])}
                       labels={label_text(modes_distance)}
                       id="all_travels_modes_distance"
                       colors={colors(modes_distance)}
                       height="450"/>
              <p className="text-center mt-3">Répartition modale en km parcourus</p>
            </div>
          </div>

        </div>
      </div>

  );
  }
}

export default Modes;
