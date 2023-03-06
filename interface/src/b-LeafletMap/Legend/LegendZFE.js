import React, { Component } from 'react';


class LegendZFE extends React.Component {
  render() {
    return(
      <div className="row mb-1 mt-1">
        <div className="col">
            <div className="row align-items-center">
              <div className="col-4 pr-0 pl-0">
                <div className="row justify-content-center">
                  <div className="col-5" style={{borderBottom: this.props.pattern.width*1.5 + "px " + this.props.pattern.legend_style + " " + this.props.pattern.color}}></div>
                </div>
              </div>

              <div className="col-8 pl-0 pr-0">
                <p><b>{this.props.name}</b></p>
              </div>
            </div>
        </div>
      </div>

    )
  }
}

export default LegendZFE;
