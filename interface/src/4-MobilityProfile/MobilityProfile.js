import React, { Component } from 'react';

import Modes from './Modes';
import Reasons from './Reasons';
import MobilityWork from './MobilityWork';
import MobilityHome from './MobilityHome';
import Zones from './Zones';
import FlowsOD_all from './FlowsOD_all';
import FlowsOD_home_work from './FlowsOD_home_work';
import FlowsOD_detailed from './FlowsOD_detailed';

import SourcesRow from '../f-Utilities/SourcesRow'
import SourcesP from '../f-Utilities/SourcesP'
import Info from '../f-Utilities/Info'

import PlotPie from '../c-PlotlyFigures/PlotPie';

import {formatFigure} from '../f-Utilities/util_func';

class MobilityProfile extends React.Component {
  constructor(props){
    super(props)

    this.state = {
      selected_focus: "focus_work"
    }
  }

  setFocus = (focus) => {
    this.setState({selected_focus: focus})
  }

  render() {

    function label_text(status){
      var total = Object.values(status).reduce((a,b) => a + b);
      var text = Object.fromEntries(
                  Object.entries(status).map(
                    ([k, v], i) => [k, "<span style='font-size: 1.5vw;'>" + Math.round(v/total*1000)/10 +
                                      " %</span></br></br><span style='font-weight: 300;'>" + k + "</span>" ]
                  )
                );
      return(Object.values(text))
    }

    function hover_text(status){
      var text = Object.fromEntries(
                  Object.entries(status).map(
                    ([k, v], i) => [k, k + "</br></br><span style='font-weight: 300;'>" + Math.round(v) + " déplacements</span>"]
                  )
                );
      return(Object.values(text))
    }

    let territory = this.props.territory;
    let key_figures_total = territory.travels_analysis["1_key_figures"].total

    let total_number = key_figures_total.number == null ? "/" : formatFigure(key_figures_total.number, 3)
    let nb_per_mob_pers = key_figures_total.number_per_mob_pers == null ? "/" : formatFigure(key_figures_total.number_per_mob_pers, 3)
    let dist_per_mob_pers = key_figures_total.distance_per_mob_pers == null ? "/" : formatFigure(key_figures_total.distance_per_mob_pers, 3)
    let duration_per_mob_pers = key_figures_total.duration_per_mob_pers == null ? "/" : formatFigure(key_figures_total.duration_per_mob_pers, 2)

    var SIGNIFICANCE_THRESHOLD = 30

    return(
      <div className="row">
        <div className="col">

          <div className="row justify-content-between mb-5">
            <div className="col-3">
              <p className="mb-3">On quantifie ici les déplacements de la population du territoire, un jour de semaine moyen. <Info content="Il s'agit des déplacements de la population de 6 ans inclus et plus. On étudie uniquement les déplacements hors périodes de vacances scolaires. On se restreint aux déplacements du quotidien, c'est à dire aux déplacements qui s'effectuent à moins de 80km à vol d'oiseau du domicile."/></p>
              <p><span className="key_figure">{total_number}</span> déplacements/jour</p>
              <p>→ <b>{nb_per_mob_pers}</b> déplacements/jour/personne mobile</p>
              <p>→ <b>{dist_per_mob_pers}</b> km/jour/personne mobile</p>
              <p className="mb-3">→ <b>{duration_per_mob_pers}</b> min/jour/personne mobile</p>

              {Object.keys(this.props.territory.sources).includes("emd") ?
              <SourcesP sources={this.props.territory.sources}
                     concerned={["emd"]}/> :
               <SourcesP sources={this.props.territory.sources}
                      concerned={["entd", "census", "mobpro", "bpe"]} processed={true}/>
              }
            </div>
            <div className="col-4">
              <Modes territory={territory} />
              <div className="row mt-4"></div>
              {Object.keys(this.props.territory.sources).includes("emd") ?
                <SourcesRow sources={this.props.territory.sources}
                       concerned={["emd"]}/> :
                 <SourcesRow sources={this.props.territory.sources}
                        concerned={["entd", "census", "mobpro", "bpe"]} processed={true}/>}

            </div>
            <div className="col-4">
              <Reasons territory={territory} />
              <div className="row mt-4"></div>
              {Object.keys(this.props.territory.sources).includes("emd") ?
                <SourcesRow sources={this.props.territory.sources}
                       concerned={["emd"]}/> :
                 <SourcesRow sources={this.props.territory.sources}
                        concerned={["entd", "census", "mobpro", "bpe"]} processed={true}/>}

            </div>
          </div>

          <Zones territory={territory} significance_threshold={SIGNIFICANCE_THRESHOLD} id="zones" />

          {territory.travels_analysis["3_flows"].flows_commune_all["number"].length > 0 ?
            <div>
              <FlowsOD_all territory={territory} id="all_flows_od"/>
              <FlowsOD_detailed territory={territory} id="all_flows_od_detailed" significance_threshold={SIGNIFICANCE_THRESHOLD}/>
            </div>
            : <p>Aucun flux significatifs entre communes à afficher.</p>
          }

          {/*<FlowsOD_home_work territory={territory} id="all_flows_od_home_work"/>*/}

          <div className="row mt-5 mb-4">
            <div className="col">
                <div className="row">
                  <div className="col-auto">
                    <h3 onClick={this.setFocus.bind(this, "focus_work")}
                        className={this.state.selected_focus == "focus_work" ? "mb-0 pb-1 nav selected" : "mb-0 pb-1 nav"}>FOCUS SUR LES TRAJETS DOMICILE ↔ TRAVAIL</h3>
                  </div>
                  <div className="col-auto">
                    <h3 onClick={this.setFocus.bind(this, "focus_home")}
                        className={this.state.selected_focus == "focus_home" ? "mb-0 pb-1 nav selected" : "mb-0 pb-1 nav"}>FOCUS SUR LES TRAJETS DOMICILE ↔ autre motif que travail</h3>
                  </div>
                </div>
            </div>
          </div>

          {this.state.selected_focus == "focus_home" ?
              <MobilityHome territory={territory} /> :
              <MobilityWork territory={territory} />}

        </div>
      </div>
    )
  }
}

export default MobilityProfile;
