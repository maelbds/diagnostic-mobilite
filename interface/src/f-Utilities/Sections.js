import React, { Component } from 'react';

import {c_light, c_dark} from '../a-Graphic/Colors';

class Sections extends React.Component{
  constructor(props) {
   super(props);
  }

  render(){
    return(
      <div className="row mt-5 mb-5">
        <div className="col">
                <div className="row">
                  {this.props.dev_mode && <div className="col-auto">
                    <h2 onClick={this.props.setSection.bind(this, "dev")}
                        className={this.props.selectedSection == "dev" ? "mb-0 pb-1 nav selected" : "mb-0 pb-1 nav"}>dev</h2>
                  </div>}
                  <div className="col-auto">
                    <h2 onClick={this.props.setSection.bind(this, "territory")}
                        className={this.props.selectedSection == "territory" ? "mb-0 pb-1 nav selected" : "mb-0 pb-1 nav"}>description du territoire</h2>
                  </div>
                  <div className="col-auto">
                    <h2 onClick={this.props.setSection.bind(this, "offer")}
                        className={this.props.selectedSection == "offer" ? "mb-0 pb-1 nav selected" : "mb-0 pb-1 nav"}>offre de transport</h2>
                  </div>
                  <div className="col-auto">
                    <h2 onClick={this.props.setSection.bind(this, "mobility")}
                        className={this.props.selectedSection == "mobility" ? "mb-0 pb-1 nav selected" : "mb-0 pb-1 nav"}>pratiques de déplacement</h2>
              </div>
            </div>

        </div>
      </div>
    );
  }
}

export default Sections;
