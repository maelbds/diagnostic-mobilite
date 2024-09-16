import React, { Component } from 'react';
import * as d3 from "d3";

import LoadingChart from '../f-Utilities/LoadingChart';
import SourcesRow from '../f-Utilities/SourcesRow';
import Info from '../f-Utilities/Info';

import {api_call} from '../0-Home/api';
import {formatFigure} from '../f-Utilities/util_func';


class KeyFigures extends React.Component {
  constructor(props){
    super(props)

    this.state = {
      status: "loading",
      data: {
        "total_nb": "--",
        "total_dist": "--",
        "total_dist_pers": "--",
        "total_nb_pers": "--",
        "sources": []
      },
    }
  }

  componentDidMount(){
    let endpoints = ["mobility/key_figures"]
    api_call.call(this, endpoints)
  }

  render() {
    let {total_nb, total_dist, total_dist_pers, total_nb_pers, sources} = this.state.data;

    return(
      <div className="row justify-content-start mb-5">
        <div className="col-9">
          <div className="row">
            <div className="col-4">
              <p className="mb-3">On quantifie dans cette section les déplacements de la population du territoire, un jour de semaine moyen. <Info content="Il s'agit des déplacements de la population de 6 ans inclus et plus. On étudie uniquement les déplacements hors périodes de vacances scolaires. On se restreint aux déplacements du quotidien, c'est à dire aux déplacements qui s'effectuent à moins de 80km à vol d'oiseau du domicile."/></p>
            </div>

            <div className="col-8">
              <p><span className="key_figure">{total_nb === "--" ? "--" : formatFigure(parseFloat(parseFloat(total_nb).toPrecision(3)))}</span> déplacements/jour, soit <b>{total_dist === "--" ? "--" : formatFigure(parseFloat(parseFloat(total_dist).toPrecision(3)))}</b> passagers.km/jour</p>
              <p>→ <b>{formatFigure(total_nb_pers)}</b> déplacements/jour/personne mobile</p>
              <p>→ <b>{formatFigure(total_dist_pers)}</b> km/jour/personne mobile</p>
              {/*<p className="mb-3">→ <b>{total_duration_pers}</b> min/jour/personne mobile</p>*/}

              <SourcesRow selected_sources={sources}/>
            </div>
          </div>

        </div>
      </div>


    )
  }
}

export default KeyFigures;
