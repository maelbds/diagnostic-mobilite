import React, { Component } from 'react';


class LoadingChart extends React.Component {

  render() {
      return(
        <div className="row justify-content-center align-items-center" style={{position: "absolute", top: 0, zIndex: 100, width: "100%", height: "100%"}}>
          <div className="col-auto">
            <div className="spinner-grow" role="status">
              <span className="sr-only">Chargement...</span>
            </div>
          </div>
        </div>
      )
  }
}

export default LoadingChart;
