import React, { Component } from 'react';
import {c_light} from '../a-Graphic/Colors';
import {map_ratio, layout_ratio} from '../a-Graphic/Layout'


class Loading extends React.Component {

  render() {
    if(this.props.loading){
      return(
        <div className="row align-items-center justify-content-center ml-0" style={{height: this.props.height, backgroundColor: c_light+"66"}}>
          <div className="col-auto">
            <div className="spinner-grow" role="status">
              <span className="sr-only">Chargement...</span>
            </div>
          </div>
        </div>
      )
    } else {
      return(
        <div className="row align-items-center ml-0" style={{height: this.props.height, backgroundColor: c_light+"b3"}}>
          <div className="col">
            <p className="mb-2">Oups :(</p>
            <p>Message d'erreur : {this.props.error}</p>
          </div>
        </div>
      )
    }
  }
}

export default Loading;

Loading.defaultProps = {
  height: window.screen.width*layout_ratio*map_ratio
}
