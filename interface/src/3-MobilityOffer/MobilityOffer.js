import React, { Component } from 'react';

import PublicTransport from './PublicTransport';
import CarFleet from './CarFleet';
import CyclingFacilities from './CyclingFacilities';
import OtherFacilities from './OtherFacilities';

class MobilityOffer extends React.Component {

  render() {
    return(
      <div className="row">
        <div className="col">

          <CarFleet territory={this.props.territory} id="car_fleet" />

          <PublicTransport territory={this.props.territory} id="pt_detailed" />

          <CyclingFacilities territory={this.props.territory} id="cycling_facilities" />

          <OtherFacilities territory={this.props.territory} id="other_facilities" />

        </div>
      </div>
    )
  }
}

export default MobilityOffer;
