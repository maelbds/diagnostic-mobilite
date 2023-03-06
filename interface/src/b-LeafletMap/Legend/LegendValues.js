import React, { Component } from 'react';

import {c_missing_data} from '../../a-Graphic/Colors';

class LegendValues extends React.Component {
  render() {
    return(
      <div className="row mb-1 mt-1">
        <div className="col">
          {this.props.intervals.map((value, i)=>
            <div className="row align-items-center">

              <div className="col-4 pr-0 pl-0">
                  <p className="text-center">
                    <span className="legend_color_circles align-middle"
                          style={{backgroundColor: this.props.colors[i]}}></span>
                  </p>
              </div>

              <div className="col-8 pl-0 pr-0">
                <p>{value}</p>
              </div>

            </div>
          )
          }
          {this.props.missing_data &&
              <div className="row align-items-center">

                <div className="col-4 pr-0 pl-0">
                    <p className="text-center">
                      <span className="legend_color_circles align-middle"
                            style={{backgroundColor: c_missing_data}}></span>
                    </p>
                </div>

                <div className="col-8 pl-0 pr-0">
                  <p>donnée indisponible</p>
                </div>

              </div>
            }

        </div>
      </div>
    )
  }
}

export default LegendValues;
