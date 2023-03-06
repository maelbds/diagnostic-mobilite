import React, { Component } from 'react';

import ResidentialAreas from './ResidentialAreas';

class TerritoryProfile extends React.Component {
  render() {
    return(
      <div className="row">
        <div className="col">

          <ResidentialAreas territory={this.props.territory} id="residential_areas" />


        </div>
      </div>
    )
  }
}

export default TerritoryProfile;
