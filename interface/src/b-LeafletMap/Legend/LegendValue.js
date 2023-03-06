import React, { Component } from 'react';

import {c_missing_data} from '../../a-Graphic/Colors';

class LegendValue extends React.Component {
  render() {
    return(
      <div className="row mb-1 mt-1">
        <div className="col">
            <div className="row align-items-center">

              <div className="col-4 pr-0 pl-0">
                  <p className="text-center">
                    <span className="legend_color_circles align-middle"
                          style={{backgroundColor: this.props.color}}></span>
                  </p>
              </div>

              <div className="col-8 pl-0 pr-0">
                <p>{this.props.value}</p>
              </div>

            </div>
        </div>
      </div>
    )
  }
}

export default LegendValue;
