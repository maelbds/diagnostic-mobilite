import React from 'react';

import {c_modes} from '../a-Graphic/Colors';
import {formatFigure} from '../f-Utilities/util_func';

import SourcesRow from '../f-Utilities/SourcesRow'

import PlotPie from '../c-PlotlyFigures/PlotPie'

function MobilityGeneral(props){
    function label_text(array){
      var total = array.map((a)=>a[1]).reduce((a,b) => a + b);
      var text = array.map((a) => "<span style='font-size: 20px;'>" + formatFigure(a[1]/total*100, 2) +
                                      " %</span></br></br><span style='font-weight: 300;'>" + a[0] + "</span>");
      return text
    }

    function hover_text(array){
      var text = array.map((a) => a[0] + "</br></br><span style='font-weight: 300;'>" + formatFigure(a[1], 3) + " déplacements</span>");
      return text
    }

    function colors(array, colors){
      return array.map((a)=> colors[a[0]])
    }

    function sort_array(array, by){
      let order = {}
      Object.keys(by).map((key, i)=> order[key] = i)

      function comparison(r1, r2){
        return order[r1[0]] - order[r2[0]]
      }
      return array.sort(comparison)
    }

    let territory = props.territory;

    let modes_number = territory.travels_analysis["1_key_figures"].modes.number;
    modes_number = Object.keys(modes_number).map((key)=>[key, modes_number[key]])
    modes_number = sort_array(modes_number, c_modes)

    let key_figures_total = territory.travels_analysis["1_key_figures"].total

    console.log()

    let total_number = key_figures_total.number == null ? "/" : formatFigure(key_figures_total.number, 3)
    let nb_per_hab = key_figures_total.number == null ? "/" : formatFigure(key_figures_total.number/key_figures_total.pop, 3)
    let dist_per_hab = key_figures_total.distance == null ? "/" : formatFigure(key_figures_total.distance/key_figures_total.pop, 3)

    return(
      <div className="row">
        <div className="col">
          <div className="row align-items-end" style={{marginTop: "-80px"}}>
            <div className="col-5">
              <div className="row mb-0">
                <div className="col-auto">
                  <h3 className="">mobilité</h3>
                </div>
              </div>
              <div className="row">
                <div className="col">
                  <p><span className="key_figure">{total_number}</span> déplacements/jour</p>
                  <p>→ <b>{nb_per_hab}</b> déplacements/jour/hab</p>
                  <p>→ <b>{dist_per_hab}</b> km/jour/hab</p>
                </div>
              </div>
            </div>
            <div className="col-7">
                <PlotPie values={modes_number.map((m)=>m[1])}
                         labels={label_text(modes_number)}
                         colors={colors(modes_number, c_modes)}
                         text={hover_text(modes_number)}
                         height="330"
                         id="all_travels_means"/>
            </div>
          </div>

          <div className="row mt-1"></div>
          {Object.keys(props.territory.sources).includes("emd") ?
            <SourcesRow sources={props.territory.sources}
                   concerned={["emd"]}/> :
             <SourcesRow sources={props.territory.sources}
                    concerned={["entd", "census", "mobpro", "bpe"]} processed={true}/>}

        </div>
      </div>
  );
}

export default MobilityGeneral;
