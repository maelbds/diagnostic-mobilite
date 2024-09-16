import React, { Component } from 'react';

import Perimeter from './Perimeter';
import IdentityGeneral from './IdentityGeneral';


class KeyFigures extends React.Component {

  render() {
    return(
      <div className="row">
        <div className="col">
          <div className="row">
            <div className="col-7">
                <IdentityGeneral geography={this.props.geography} />
            </div>

            <div className="col-5">
                <Perimeter  geometry={this.props.geometry}
                            styles={this.props.styles}
                            map_id="general_perimeter"/>
            </div>
          </div>

          <div className="row mt-2">
            <div className="col-12">
            </div>
          </div>

        </div>
      </div>
    )
  }
}

export default KeyFigures;
