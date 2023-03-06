import React, { Component } from 'react';

import Header from '../f-Utilities/Header';
import Sections from '../f-Utilities/Sections';
import KeyFigures from '../1-KeyFigures/KeyFigures';
import TerritoryProfile from '../2-TerritoryProfile/TerritoryProfile';
import Dev from '../6-Dev/Dev';
import MobilityOffer from '../3-MobilityOffer/MobilityOffer';
import MobilityProfile from '../4-MobilityProfile/MobilityProfile';

import GraphicChart from '../a-Graphic/GraphicChart';
import FormBanner from '../f-Utilities/FormBanner'


class Diagnostic extends React.Component {
  constructor(props) {
     super(props);
     this.state = {
       section: "territory",
     };
   }

  setSection = (section) => {
      this.setState({
        section: section,
      })
  }

  render() {
    var territory = this.props.territory;
    return(
      <div className="row">
        <div className="col">

          <Header name={territory.name}/>

          <div className="row justify-content-center mb-5">
            <div className="col-11 col-md-11">

              <KeyFigures territory={this.props.territory}/>

              <div className="row mt-5">
              </div>

              <Sections setSection={this.setSection} selectedSection={this.state.section} dev_mode={this.props.dev_mode}/>


              {this.state.section == "territory" ?
                <TerritoryProfile territory={territory}/>
              : this.state.section == "dev" ?
                <Dev territory={territory}/>
              : this.state.section == "offer" ?
                <MobilityOffer territory={territory}/>
              : territory.travels_analysis != null && <MobilityProfile territory={territory}/>
              }

              <div className="row mt-5">
              </div>

                {/*
                Ajouter :
                Crédits : mentions opensource
                QUi participe au projet
                Mention ADEME
                */}


                {this.props.graphic_chart && <GraphicChart/>}

                {this.props.form_banner_link != null && <FormBanner link={this.props.form_banner_link}/>}

            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default Diagnostic;
