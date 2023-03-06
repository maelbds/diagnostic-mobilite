import React, { Component } from 'react';

class LegendDescription extends React.Component {
  render() {
    return(
      <div className="row mb-1 mt-1">
        <div className="col">
            <div className="row align-items-center">

              <div className="col-4 pr-0 pl-0">
              </div>

              <div className="col-8 pl-0 pr-0">
                <p>{this.props.desc}</p>
              </div>

            </div>
        </div>
      </div>
    )
  }
}

export default LegendDescription;
