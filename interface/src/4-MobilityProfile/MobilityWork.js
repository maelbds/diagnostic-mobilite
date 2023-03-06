import React, { Component } from 'react';

import {c_modes, c_reasons} from '../a-Graphic/Colors';

import MobilityWorkDirectDistance from './MobilityWorkDirectDistance';
import MobilityWorkReasonDistance from './MobilityWorkReasonDistance';

import PlotBarStacked from '../c-PlotlyFigures/PlotBarStacked';
import PlotPie from '../c-PlotlyFigures/PlotPie';
import SourcesRow from '../f-Utilities/SourcesRow'

import {formatFigure} from '../f-Utilities/util_func';

class MobilityWork extends React.Component {

  render() {

    function sort_means(means){
      let means_order = {
        "voiture" : 6,
        "voiture passager": 5,
        "transport en commun": 4,
        "à pied": 3,
        "moto": 1,
        "vélo": 2,
        "autre": 0
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

    var territory = this.props.territory;
    let work_total = territory.travels_analysis["4_focus"].work.total

    let work_total_number = work_total.number == null ? "/" : formatFigure(work_total.number, 3)
    let work_total_distance = work_total.distance == null ? "/" : formatFigure(work_total.distance, 3)
    let work_dist_per_mob_pers = work_total.distance_per_mob_pers == null ? "/" : formatFigure(work_total.distance_per_mob_pers, 3)

    let modes_number = territory.travels_analysis["4_focus"].work.modes.number;
    modes_number = Object.keys(modes_number).map((key)=>[key, modes_number[key]])
    modes_number = sort_means(modes_number)

    let modes_distance = territory.travels_analysis["4_focus"].work.modes.distance;
    modes_distance = Object.keys(modes_distance).map((key)=>[key, modes_distance[key]])
    modes_distance = sort_means(modes_distance)

    return(

          <div className="row">
            <div className="col-12">
              <div className="row">
                <div className="col-8">
                  <div className="row">
                    <div className="col-9">
                      <p className="mb-3">Dans cette section, on s'intéresse spécifiquement aux déplacements ayant comme motif <span className="pl-1 pr-1" style={{backgroundColor: c_reasons["domicile ↔ travail"], color: "white"}}>domicile ↔ travail</span>, qui sont prépondérants dans l'ensemble des déplacements.</p>
                      <p className="mb-3">Ils représentent <span className="key_figure">{work_total_number}</span> déplacements/jour. Cela équivaut à {work_total_distance}km/jour soit {work_dist_per_mob_pers}km/jour en moyenne par personne active qui se déplace.</p>
                      <p>Voici comment ces déplacements se décomposent :</p>
                    </div>
                  </div>

                  <MobilityWorkDirectDistance territory={territory}/>

                </div>

                <div className="col-4">
                  <div className="row">
                    <div className="col-auto">
                      <h4 className="mb-0">modes</h4>
                    </div>
                  </div>

                  <div className="row">
                    <div className="col-6">
                      <PlotBarStacked values={modes_number.map((m)=>m[1])}
                               labels={label_text(modes_number)}
                               id="work_travels_means_2"
                               colors={colors(modes_number)}
                               height="450"/>
                      <p className="text-center mt-3">Répartition modale en nombre de déplacements pour les déplacements domicile↔travail</p>
                    </div>
                    <div className="col-6">
                      <PlotBarStacked values={modes_distance.map((m)=>m[1])}
                               labels={label_text(modes_distance)}
                               id="work_travels_means_distance"
                               colors={colors(modes_distance)}
                               height="450"/>
                      <p className="text-center mt-3">Répartition modale en km parcourus pour les déplacements domicile↔travail</p>
                    </div>
                  </div>

                  <div className="row mt-3"></div>
                  {Object.keys(territory.sources).includes("emd") ?
                    <SourcesRow sources={territory.sources}
                           concerned={["emd"]}/> :
                     <SourcesRow sources={territory.sources}
                            concerned={["entd", "census", "mobpro", "bpe"]} processed={true}/>}
                </div>

              </div>

              {/*
              <div className="row">
                <div className="col-12">
                  <MobilityWorkReasonDistance territory={territory}/>
                </div>
              </div>
              */}

            </div>
          </div>


    )
  }
}

export default MobilityWork;
