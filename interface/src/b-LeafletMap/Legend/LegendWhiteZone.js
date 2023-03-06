import React, { Component } from 'react';
import {wz_size, wz_color_limit1, wz_color_limit2} from '../../a-Graphic/Layout';


class LegendWhiteZone extends React.Component {
  render() {
    var circle_size = wz_size*2-7
    return(
      <div className="row mb-1 mt-1">
        <div className="col">
          <div className="row mb-2">
            <div className="col-4">
            </div>
            <div className="col-8 pl-0 pr-0">
              <p><b>Zones blanches</b></p>
              <p>{this.props.label!=null && this.props.label}</p>
            </div>
          </div>

          <div className="row align-items-center mb-1">
            <div className="col-4">
                <p className="text-center">
                  <span className="legend_color_circles_wz align-middle"
                        style={{backgroundColor: wz_color_limit1,
                                height: circle_size,
                                width: circle_size }}></span>
                </p>
            </div>

            <div className="col-8 pl-0 pr-0">
              <p>entre {this.props.limit1} km et {this.props.limit2} km</p>
            </div>
          </div>

          <div className="row align-items-center">
            <div className="col-4">
                <p className="text-center">
                  <span className="legend_color_circles_wz align-middle"
                        style={{backgroundColor: wz_color_limit2,
                                height: circle_size,
                                width: circle_size }}></span>
                </p>
            </div>

            <div className="col-8 pl-0 pr-0">
              <p>plus de {this.props.limit2} km</p>
            </div>
          </div>

        </div>
      </div>
    )
  }
}

export default LegendWhiteZone;
