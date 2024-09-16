import React, { Component } from 'react';

import MainDataJig from '../g-Components/MainDataJig';
import CrossDataJig from '../g-Components/CrossDataJig';


import {population} from './population';

import {gridded_pop} from './gridded_pop';
import {gridded_hh} from './gridded_hh';
import {gridded_surf} from './gridded_surf';

import {pop_age} from './pop_age';
import {pop_status} from './pop_status';
import {pop_csp} from './pop_csp';

import {incomes_median} from './incomes_median';
import {gridded_incomes} from './gridded_incomes';
import {incomes_gini} from './incomes_gini';
import {incomes_decile_ratio} from './incomes_decile_ratio';

import {precariousness_fuel} from './precariousness_fuel';
import {precariousness_fuel_home} from './precariousness_fuel_home';

import {jobs} from './jobs';
import {work_flows} from './work_flows';
import {work_flows_outside} from './work_flows_outside';

import {places_education} from './places_education';
import {places_health} from './places_health';
import {places_grocery} from './places_grocery';
import {places_services_cluster} from './places_services_cluster';


import {aucun} from './aucun';

import {public_transport} from '../3-MobilityOffer/public_transport';


import {createFilterObject, getFiltersFromIndicators} from '../h-Filters/Filter';


class TerritoryProfile extends React.Component {
  constructor(props) {
   super(props);

   // init filters
   let all_indicators = this.all_indicators = [population, pop_age, pop_status, pop_csp,
     gridded_pop, gridded_hh, gridded_surf,
     incomes_median, gridded_incomes, incomes_gini, incomes_decile_ratio,
     precariousness_fuel, precariousness_fuel_home,
     jobs, work_flows, work_flows_outside,
     places_education, places_health, places_grocery, places_services_cluster,
     public_transport, aucun
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

        {/*<CrossDataJig geometry={geometry}
                     geography={geography}

                    title={"carte à la carte"}
                    map_id={"custom"}

                    indicators={[aucun, population, pop_age, pop_status, gridded_pop, public_transport]}
                    indicator_init={{
                      choropleth: [pop_age],
                      circle: [population],
                      path: [],
                    }}

                     styles={this.props.styles}
                     com_topo={this.props.com_topo}

                    filters={createFilterObject.call(this, getFiltersFromIndicators([population, pop_age, pop_status, gridded_pop, public_transport]))}
                    />*/}

        <MainDataJig geometry={geometry}
                     geography={geography}

                    title={"organisation géographique de la population"}
                    map_id={"pop_geo"}

                    indicators={[
                                  {name: null, indicators: [population, gridded_pop, gridded_hh, gridded_surf]}
                                ]}
                    indicator_init={population}

                    styles={this.props.styles}

                    filters={createFilterObject.call(this, getFiltersFromIndicators([population, gridded_pop, gridded_hh, gridded_surf]))}
                    />

        <MainDataJig geometry={geometry}
                     geography={geography}

                    title={"profil de la population"}
                    map_id={"pop_profile"}

                    indicators={[
                                  {name: null, indicators: [pop_age, pop_status, pop_csp]},
                                ]}
                    indicator_init={pop_age}

                    styles={this.props.styles}

                    filters={createFilterObject.call(this, getFiltersFromIndicators([pop_age, pop_csp, pop_status]))}
                    />

        <MainDataJig geometry={geometry}
                     geography={geography}

                    title={"REVENUS ET INÉGALITÉS"}
                    map_id={"incomes"}

                    indicators={[
                                  {name: null, indicators: [incomes_median, gridded_incomes, incomes_gini, incomes_decile_ratio]},
                                ]}
                    indicator_init={incomes_median}

                    styles={this.props.styles}

                    filters={createFilterObject.call(this, getFiltersFromIndicators([]))}
                    />


        <MainDataJig geometry={geometry}
                     geography={geography}

                    title={"PRÉCARITÉ ÉNERGÉTIQUE"}
                    map_id={"precariousness"}

                    indicators={[
                                  {name: null, indicators: [precariousness_fuel, precariousness_fuel_home]},
                                ]}
                    indicator_init={precariousness_fuel}

                    styles={this.props.styles}

                    filters={createFilterObject.call(this, getFiltersFromIndicators([]))}
                    />

        <MainDataJig geometry={geometry}
                     geography={geography}

                    title={"emploi"}
                    map_id={"jobs"}

                    indicators={[
                                  {name: null, indicators: [jobs, work_flows, work_flows_outside]},
                                ]}
                    indicator_init={jobs}

                    styles={this.props.styles}

                    filters={createFilterObject.call(this, getFiltersFromIndicators([work_flows, work_flows_outside]))}
                    />

        <MainDataJig geometry={geometry}
                     geography={geography}

                    title={"activités"}
                    map_id={"activities"}

                    indicators={[
                                  {name: null, indicators: [places_education, places_health, places_grocery, places_services_cluster]},
                                ]}
                    indicator_init={places_education}

                    styles={this.props.styles}

                    filters={createFilterObject.call(this, getFiltersFromIndicators([]))}
                    />


            <div className="row justify-content-end mt-5 mb-5">
              <div className="col-auto">
                <p class="button p-1 pl-2 pr-2" onClick={this.props.setSection.bind(this, "offer")}>Offre de transport →</p>
              </div>
            </div>
        </div>
      </div>
    )
  }
}

export default TerritoryProfile;
