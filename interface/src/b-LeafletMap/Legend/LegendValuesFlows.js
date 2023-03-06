import React, { Component } from 'react';


class LegendValuesFlows extends React.Component {
  render() {
    return(
      <div className="row mb-1 mt-1">
        <div className="col">
          {this.props.intervals.map((value, i)=>
            <div className="row align-items-center">

              <div className="col-4 pr-0 pl-0">
                <div className="row justify-content-center">
                  <div className="col-5" style={{backgroundColor: this.props.colors[i], height: 4 + i*2.5 + "px"}}></div>
                </div>
              </div>

              <div className="col-8 pl-0 pr-0">
                <p>{value}</p>
              </div>

            </div>
          )
          }
        </div>
      </div>

    )
  }
}

export default LegendValuesFlows;
