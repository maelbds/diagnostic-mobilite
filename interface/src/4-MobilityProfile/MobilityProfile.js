import React, { Component } from 'react';

import SourcesRow from '../f-Utilities/SourcesRow'
import SourcesP from '../f-Utilities/SourcesP'
import Info from '../f-Utilities/Info'

import Note from './Note';
import KeyFigures from './KeyFigures';
import Modes from './Modes';
import Reasons from './Reasons';
import MobilityHome from './MobilityHome';
import MobilityWork from './MobilityWork';

import MainDataJig from '../g-Components/MainDataJig';
import {createFilterObject, getFiltersFromIndicators} from '../h-Filters/Filter';

import {flows} from './flows';


class MobilityProfile extends React.Component {
  constructor(props){
    super(props)

    // init filters
    let all_indicators = this.all_indicators = [flows];
    all_indicators.map(ind => ind.setDatasets(this.props.datasets))

    let all_filters = getFiltersFromIndicators(all_indicators)
    this.state = Object.assign({
      selected_focus: "focus_work"
    },
      ...all_filters.map(f => f.initFilter())
    );
  }

  updateFilter = (filter) => {
   return (prev_selected, selection) => {
     this.setState(filter.updateFilter(prev_selected, selection))
   }
  }

  setFocus = (focus) => {
    this.setState({selected_focus: focus})
  }


  render() {
    let {geography, geometry, styles} = this.props;

    return(

    <div className="row">
      <div className="col">

        <Note geography={geography}/>

        <KeyFigures geography={geography}/>

        <div className="row mb-5">

          <div className="col-12 col-md-6">
            <Modes geography={geography}/>
          </div>

          <div className="col-12 col-md-6">
            <Reasons geography={geography}/>
          </div>

        </div>

        <MainDataJig geometry={geometry}
                     geography={geography}

                    title={"flux"}
                    map_id={"all_flows"}

                    indicators={[
                                  {name: null, indicators: [flows]}
                                ]}
                    indicator_init={flows}

                    styles={styles}

                    filters={createFilterObject.call(this, getFiltersFromIndicators([flows]))}
                    />

        <div className="row mt-5 mb-4">
          <div className="col-auto">
            <h3 onClick={this.setFocus.bind(this, "focus_work")}
                className={this.state.selected_focus == "focus_work" ? "mb-0 pb-1 nav selected" : "mb-0 pb-1 nav"}>FOCUS SUR LES TRAJETS DOMICILE ↔ TRAVAIL</h3>
          </div>
          <div className="col-auto">
            <h3 onClick={this.setFocus.bind(this, "focus_home")}
                className={this.state.selected_focus == "focus_home" ? "mb-0 pb-1 nav selected" : "mb-0 pb-1 nav"}>FOCUS SUR LES TRAJETS DOMICILE ↔ autre motif que travail</h3>
          </div>
        </div>

        {this.state.selected_focus == "focus_home" ?
            <MobilityHome geography={geography} /> :
            <MobilityWork geography={geography} />}

        <div className="row mb-5">
          <div className="col">
          </div>
        </div>
        <div className="row mb-5">
          <div className="col">
          </div>
        </div>


        <div className="row justify-content-start mt-5 mb-5">
          <div className="col-auto">
            <p class="button p-1 pl-2 pr-2" onClick={this.props.setSection.bind(this, "offer")}>← Offre de transport</p>
          </div>
        </div>


      </div>
    </div>
    )



          {/*

          <Zones territory={territory} significance_threshold={SIGNIFICANCE_THRESHOLD} id="zones" />*/}

          {/*territory.travels_analysis["3_flows"].flows_commune_all["number"].length > 0 ?
            <div>
              <FlowsOD_all territory={territory} id="all_flows_od"/>
              <FlowsOD_detailed territory={territory} id="all_flows_od_detailed" significance_threshold={SIGNIFICANCE_THRESHOLD}/>
            </div>
            : <p>Aucun flux significatifs entre communes à afficher.</p>
          }

          {/*<FlowsOD_home_work territory={territory} id="all_flows_od_home_work"/>*/}
  }
}

export default MobilityProfile;
