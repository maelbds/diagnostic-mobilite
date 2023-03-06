import React from 'react';

import PlotPie from '../c-PlotlyFigures/PlotPie'
import Info from '../f-Utilities/Info'
import SourcesP from '../f-Utilities/SourcesP'

import {formatFigure} from '../f-Utilities/util_func';

function IdentityGeneral(props){
  function label_text(status){
    var total = Object.values(status).reduce((a,b) => a + b);
    var text = Object.fromEntries(
                Object.entries(status).map(
                  ([k, v], i) => [k, "<span style='font-size: 22px;'>" + formatFigure(v/total*100, 2) +
                                    " %</span></br></br><span style='font-weight: 300;'>" + k + "</span>" ]
                )
              );
    return(Object.values(text))
  }

  function hover_text(status){
    var text = Object.fromEntries(
                Object.entries(status).map(
                  ([k, v], i) => [k, k + "</br></br><span style='font-weight: 300;'>" + formatFigure(v) + " personnes</span>"]
                )
              );
    return(Object.values(text))
  }

    var full_status = props.territory.pop_status
    var light_status = {
      "actifs & actives": full_status.employed,
      "au chômage": full_status.unemployed,
      "à la retraite": full_status.retired,
      "scolaires": full_status.scholars_2_5 +
                full_status.scholars_6_10 +
                full_status.scholars_11_14 +
                full_status.scholars_15_17 +
                full_status.scholars_18,
      "autres": full_status.other
    }

    return(

<div className="row">
  <div className="col">
    <div className="row mb-0">
      <div className="col-auto">
      <h3 className="">identité du territoire</h3>
      </div>
    </div>
    <div className="row no-gutters justify-content-left">
      <div className="col-6">
        <p><span className="key_figure">{formatFigure(props.territory.population)}</span> habitant.es </p>
        <p className="mb-2">pour <b>{formatFigure(props.territory.households_nb)}</b> ménages</p>

        <PlotPie values={Object.values(light_status)}
                 labels={label_text(light_status)}
                 text={hover_text(light_status)}
                 height={280}
                 id="pop_status"/>

      </div>
      <div className="col-6">
          <p><span className="key_figure">{formatFigure(props.territory.jobs_nb)}</span> emplois sur le territoire</p>
          <p>soit un <b>indicateur de concentration d'emploi de {Math.round(props.territory.jobs_nb/props.territory.pop_status.employed * 100)}
          </b> <Info content="L'indicateur de concentration d'emploi est égal au nombre d'emplois dans la zone pour 100 actifs ayant un emploi résidant dans la zone (définition INSEE)."/>
          </p>

          <p className="mt-2"><span className="key_figure">{props.territory.motorisation_rate} %</span> des ménages sont motorisés</p>
          <p className="mt-2 mb-2">Une densité de <span className="key_figure">{formatFigure(props.territory.density)}</span> hab/km²</p>
          <SourcesP sources={props.territory.sources} concerned={["dossier_complet", "surface"]}/>
       </div>
     </div>
   </div>
  </div>

  );
}

export default IdentityGeneral;
