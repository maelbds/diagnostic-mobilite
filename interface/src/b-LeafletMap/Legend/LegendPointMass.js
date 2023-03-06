import React, { Component } from 'react';

import {c_yellow} from '../../a-Graphic/Colors';

class LegendPointMass extends React.Component {
  render() {
    return(
      <div className="row align-items-center mb-1 mt-1">

        <div className="col-4 pr-0 pl-0">
            <p className="text-center">
              <span className="legend_cluster_area align-middle"
                    style={{height: "40px", width: "40px",
                            backgroundColor: this.props.color==null ? c_yellow : this.props.color}}></span>
            </p>
        </div>

        <div className="col-8 pl-0 pr-0">
          <p className=""><b>{this.props.label}</b></p>
          {this.props.unit != null && <p><i>{this.props.unit}</i></p>}
        </div>
      </div>
    )
  }
}

export default LegendPointMass;
