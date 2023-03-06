import React, { Component } from 'react';

import PopulationOrganization from './PopulationOrganization';
import PopulationProfile from './PopulationProfile';
import Incomes from './Incomes';
import Precariousness from './Precariousness';
import Organization from './AAV';
import Work from './Work';
import Activities from './Activities';

class TerritoryProfile extends React.Component {
  render() {
    return(
      <div className="row">
        <div className="col">

          <PopulationOrganization territory={this.props.territory} />

          <PopulationProfile territory={this.props.territory} />

          <Incomes territory={this.props.territory} id="incomes" />

          <Precariousness territory={this.props.territory} id="incomes" />

          {/*<Organization territory={this.props.territory} id="organization" />*/}

          <Work territory={this.props.territory} />

          <Activities territory={this.props.territory} />

        </div>
      </div>
    )
  }
}

export default TerritoryProfile;
