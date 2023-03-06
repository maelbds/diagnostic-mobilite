import React, { Component } from 'react';

import {c_yellow} from '../../a-Graphic/Colors';


class LegendRoute extends React.Component {
  render() {
    return(
      <div className="row align-items-center mb-1 mt-1">

        <div className="col-4 pr-0 pl-0">

          {this.props.color.map((value, i)=>
            <p className="text-center">
              <span className="legend_route align-middle"
                    style={{height: this.props.size==null ? "25px" : this.props.size + "px",
                            width: "40px",
                            backgroundColor: value,
                            }}></span>
            </p>
          )}
        </div>

        <div className="col-8 pl-0 pr-0">
          <p className=""><b>{this.props.label==null ? "" : this.props.label}</b></p>
        </div>
      </div>
    )
  }
}

export default LegendRoute;
