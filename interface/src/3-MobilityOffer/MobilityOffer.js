import React, { Component } from 'react';

import MainDataJig from '../g-Components/MainDataJig';

import {public_transport} from './public_transport';

import {households_motorisation} from './households_motorisation';
import {critair} from './critair';

import {cycle} from './cycle';

import {bnlc} from './bnlc';
import {irve} from './irve';

import {createFilterObject, getFiltersFromIndicators} from '../h-Filters/Filter';


class MobilityOffer extends React.Component {
  constructor(props) {
   super(props);

   // init filters
   let all_indicators = this.all_indicators = [public_transport,
     households_motorisation, critair,
     cycle,
     bnlc, irve
   ];
   all_indicators.map(ind => ind.setDatasets(this.props.datasets))

   let all_filters = getFiltersFromIndicators(all_indicators)
   this.state = Object.assign({},
     ...all_filters.map(f => f.initFilter())
   );
  }

  updateFilter = (filter) => {
    return (prev_selected, selection) => {
      this.setState(filter.updateFilter(prev_selected, selection))
    }
  }

  render() {
    let {geography, geometry, datasets} = this.props

    return(
      <div className="row">
        <div className="col">

          <MainDataJig geometry={geometry}
                       geography={geography}

                      title={"parc automobile"}
                      map_id={"car_fleet"}

                      indicators={[
                                    {name: null, indicators: [households_motorisation, critair]},
                                  ]}
                      indicator_init={households_motorisation}

                      styles={this.props.styles}

                      filters={createFilterObject.call(this, getFiltersFromIndicators([critair]))}
                      />

          <MainDataJig geometry={geometry}
                       geography={geography}

                      title={"transports en commun"}
                      map_id={"public_transport"}

                      indicators={[
                                    {name: null, indicators: [public_transport]},
                                  ]}
                      indicator_init={public_transport}

                      styles={this.props.styles}

                      filters={createFilterObject.call(this, getFiltersFromIndicators([public_transport]))}
                      />

          <MainDataJig geometry={geometry}
                       geography={geography}

                      title={"mobilités actives"}
                      map_id={"active_mode"}

                      indicators={[
                                    {name: null, indicators: [cycle]},
                                  ]}
                      indicator_init={cycle}

                      styles={this.props.styles}

                      filters={createFilterObject.call(this, getFiltersFromIndicators([]))}
                      />

          <MainDataJig geometry={geometry}
                       geography={geography}

                      title={"autres infrastructures"}
                      map_id={"bnlc_irve"}

                      indicators={[
                                    {name: null, indicators: [irve, bnlc]},
                                  ]}
                      indicator_init={irve}

                      styles={this.props.styles}

                      filters={createFilterObject.call(this, getFiltersFromIndicators([]))}
                      />

          <div className="row justify-content-between mt-5 mb-5">
            <div className="col-auto">
              <p class="button p-1 pl-2 pr-2" onClick={this.props.setSection.bind(this, "territory")}>← Description du territoire</p>
            </div>
            <div className="col-auto">
              <p class="button p-1 pl-2 pr-2" onClick={this.props.setSection.bind(this, "mobility")}>Pratiques de déplacement →</p>
            </div>
          </div>

        </div>
      </div>
    )
  }
}

export default MobilityOffer;
