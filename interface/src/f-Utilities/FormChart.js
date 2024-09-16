import React, { Component } from 'react';

import {c_gradient_reds} from '../a-Graphic/Colors'

class FormChart extends React.Component {
  constructor(props) {
    super(props);
  }

  linkAndClose = () => {
    window.open(this.props.link, '_blank').focus();
    this.props.setFormChart(false)
  }

  render() {
    if (this.props.form_chart_active){
      return(
        <div className="row fixed-top align-items-center justify-content-center" style={{backgroundColor: "rgba(0, 0, 0, 0.5)", zIndex: 5001, height: "100%"}}>
         <div className="col-10 col-md-4 p-2 px-3 popup_form_chart">
          <h3>Charte d'utilisation</h3>
          <p className="mb-2">L'outil Diagnostic Mobilité est une ressource commune mise à disposition librement.
          Pour assurer sa pérennité, il est essentiel de savoir comment cette ressource est utilisée.</p>

          <p onClick={this.linkAndClose}
             className={"button p-1 pl-3 pr-3"}>En accédant au diagnostic, je m'engage à répondre au formulaire sur mon usage de l'outil.</p>

           <p className="sources mt-3">Le formulaire est également accessible en cliquant sur la bannière orange en bas de l'outil ↓</p>
         </div>
        </div>
      )
    }
  }
}

export default FormChart;
