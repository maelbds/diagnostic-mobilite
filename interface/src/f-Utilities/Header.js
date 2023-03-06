import React, { Component } from 'react';

import {c_light, c_dark} from '../a-Graphic/Colors';

class Header extends React.Component{
  constructor(props) {
   super(props);
  }

  render(){
    return(
      <div className="row mb-5">
        <div className="col">

            <div className="row justify-content-center" style={{backgroundColor: c_light}}>
              <div className="col-11 col-md-11">
                <div className="row mb-4">
                </div>
                <div className="row justify-content-between">
                  <div className="col-auto">
                    <h1 className="mb-0">diagnostic mobilité</h1>
                    <p className="mb-0 pb-2"> Comprendre les enjeux de mobilité et évaluer des solutions adaptées pour une mobilité durable.</p>
                  </div>
                  <div className="col-4">
                    <h3 className="text-right mt-1"> {this.props.name} </h3>
                  </div>
                </div>
              </div>
            </div>

        </div>
      </div>
    );
  }
}

export default Header;
