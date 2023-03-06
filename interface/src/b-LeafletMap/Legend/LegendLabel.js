import React, { Component } from 'react';

class LegendLabel extends React.Component {
  render() {
    return(
      <div className="row mb-2 mt-1">
        <div className="col">
            <div className="row align-items-center">

              <div className="col-4 pr-0 pl-0">
              </div>

              <div className="col-8 pl-0 pr-0">
                <p><b>{this.props.label}</b> <i>{this.props.unit}</i></p>
              </div>

            </div>
        </div>
      </div>
    )
  }
}

export default LegendLabel;
