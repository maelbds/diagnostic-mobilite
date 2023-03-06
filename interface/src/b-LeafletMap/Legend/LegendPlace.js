import React, { Component } from 'react';

import Info from '../../f-Utilities/Info'

import {c_yellow} from '../../a-Graphic/Colors';


class LegendPlace extends React.Component {
  render() {
    return(
      <div className="row align-items-center mb-1 mt-1">

        <div className="col-4 pr-0 pl-0">
            <p className="text-center">
              <span className="legend_cluster_area align-middle"
                    style={{height: this.props.size==null ? "25px" : this.props.size + "px",
                            width: this.props.size==null ? "25px" : this.props.size+ "px",
                            backgroundColor: this.props.color==null ? c_yellow : this.props.color,
                            }}></span>
            </p>
        </div>

        <div className="col-8 pl-0 pr-0">
          <p className=""><b>{this.props.label==null ? "Lieux" : this.props.label}</b></p>
          {this.props.subtitle != null && <p className="">{this.props.subtitle}</p>}
          {this.props.info != null && <p><Info content={this.props.info}/></p>}
        </div>
      </div>
    )
  }
}

export default LegendPlace;
