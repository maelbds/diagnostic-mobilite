import React, { Component } from 'react';

import {c_modes, c_reasons} from '../a-Graphic/Colors';

import MobilityHomeDirectDistance from './MobilityHomeDirectDistance';
import MobilityHomeReasonDistance from './MobilityHomeReasonDistance';

import PlotBarStacked from '../c-PlotlyFigures/PlotBarStacked';
import PlotPie from '../c-PlotlyFigures/PlotPie';
import SourcesRow from '../f-Utilities/SourcesRow'

import {formatFigure} from '../f-Utilities/util_func';

class MobilityHome extends React.Component {

  render() {

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
                    (m) => "<span style='font-size: 1.5vw;'>" + formatFigure(m[1]/total*100, 2) +
                                      " %</span></br></br><span style='font-weight: 300;'>" + m[0] + "</span>"
                  );
      return text
    }
    function colors(modes){
      return modes.map((m)=> c_modes[m[0]])
    }

    var territory = this.props.territory;
    let home_total = territory.travels_analysis["4_focus"].home.total

    let home_total_number = home_total.number == null ? "/" : formatFigure(home_total.number, 3)
    let home_total_distance = home_total.distance == null ? "/" : formatFigure(home_total.distance, 3)
    let home_dist_per_mob_pers = home_total.distance_per_mob_pers == null ? "/" : formatFigure(home_total.distance_per_mob_pers, 3)

    let modes_number = territory.travels_analysis["4_focus"].home.modes.number;
    modes_number = Object.keys(modes_number).map((key)=>[key, modes_number[key]])
    modes_number = sort_modes(modes_number)

    let modes_distance = territory.travels_analysis["4_focus"].home.modes.distance;
    modes_distance = Object.keys(modes_distance).map((key)=>[key, modes_distance[key]])
    modes_distance = sort_modes(modes_distance)

    return(

      <div className="row">
        <div className="col-12">

          <div className="row">
            <div className="col-8">
              <div className="row">
                <div className="col-9">
                  <p className="mb-3">Dans cette section, on s'intéresse spécifiquement aux déplacements ayant comme motif <span className="pl-1 pr-1" style={{backgroundColor: c_reasons["domicile ↔ études"]}}>
                  domicile ↔ études</span>, <span className="pl-1 pr-1" style={{backgroundColor: c_reasons["domicile ↔ achats"]}}>
                  domicile ↔ achats</span>, <span className="pl-1 pr-1" style={{backgroundColor: c_reasons["domicile ↔ accompagnement"]}}>
                  domicile ↔ accompagnement</span>, <span className="pl-1 pr-1" style={{backgroundColor: c_reasons["domicile ↔ loisirs"]}}>
                  domicile ↔ loisirs</span>, <span className="pl-1 pr-1" style={{backgroundColor: c_reasons["domicile ↔ visites"]}}>
                  domicile ↔ visites</span>, ou <span className="pl-1 pr-1" style={{backgroundColor: c_reasons["domicile ↔ affaires personnelles"]}}>
                  domicile ↔ affaires personnelles</span>. C'est
                  à dire, les déplacements directement en lien avec le domicile, avec un motif autre que travail.</p>
                  <p className="mb-3">Ils représentent <span className="key_figure">{home_total_number}</span> déplacements/jour
                  ayant comme motif le domicile au départ ou à l'arrivée.
                  Cela équivaut à {home_total_distance} km soit {home_dist_per_mob_pers} km/jour en moyenne par personne qui se déplace.</p>
                  <p>Voici comment ces déplacements se décomposent :</p>
                </div>
              </div>

              <MobilityHomeDirectDistance territory={territory}/>

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
                           id="home_travels_means_2"
                           colors={colors(modes_number)}
                           height="450"/>
                  <p className="text-center mt-3">Répartition modale en nombre de déplacements pour les déplacements domicile ↔ autre motif que travail</p>
                </div>
                <div className="col-6">
                  <PlotBarStacked values={modes_distance.map((m)=>m[1])}
                           labels={label_text(modes_distance)}
                           id="home_travels_means_distance"
                           colors={colors(modes_distance)}
                           height="450"/>
                  <p className="text-center mt-3">Répartition modale en km parcourus pour les déplacements domicile ↔ autre motif que travail</p>
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

          <div className="row">
            <div className="col-12">
              <MobilityHomeReasonDistance territory={territory}/>
            </div>
          </div>

        </div>
      </div>


    )
  }
}

export default MobilityHome;
