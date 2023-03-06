import React, { Component } from 'react';

import {c_yellow} from '../../a-Graphic/Colors';


class LegendClusterArea extends React.Component {
  render() {
    return(
      <div className="row align-items-center">

        <div className="col-4 pr-0 pl-0">
            <p className="text-center">
              <span className="legend_cluster_area align-middle"
                    style={{backgroundColor: c_yellow,
                            width: "40px",
                            height: "40px"}}></span>
            </p>
        </div>

        <div className="col-8 pl-0 pr-0">
          <p><b>{this.props.label==null ? "Lieux" : this.props.label}</b></p>
          <p><i>{this.props.sublabel!=null && this.props.sublabel}</i></p>
        </div>
      </div>
    )
  }
}

export default LegendClusterArea;
