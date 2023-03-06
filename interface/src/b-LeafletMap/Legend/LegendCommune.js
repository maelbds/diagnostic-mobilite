import React, { Component } from 'react';


class LegendCommune extends React.Component {
  render() {
    return(
      <div className="row align-items-center mt-2 mb-2">
        <div className="col-4 pr-0 pl-0">
          <div className="row justify-content-center">
            <div className="col-auto">
              <img className="img-fluid icon_legend" src="icons/commune_green.png"/>
            </div>
          </div>
        </div>
        <div className="col-8 pl-0 pr-0">
          <p><b>Communes</b></p>
          <p>{this.props.label!=null && this.props.label}</p>
        </div>
      </div>
    )
  }
}

export default LegendCommune;
