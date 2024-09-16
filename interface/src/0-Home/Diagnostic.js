import React, { Component } from 'react';

import Header from '../f-Utilities/Header';
import Footer from '../f-Utilities/Footer';
import Sections from '../f-Utilities/Sections';
import KeyFigures from '../1-KeyFigures/KeyFigures';
import TerritoryProfile from '../2-TerritoryProfile/TerritoryProfile';
import MobilityOffer from '../3-MobilityOffer/MobilityOffer';
import MobilityProfile from '../4-MobilityProfile/MobilityProfile';

import GraphicChart from '../a-Graphic/GraphicChart';
import FormBanner from '../f-Utilities/FormBanner';
import FormChart from '../f-Utilities/FormChart';

import {computeGeometry} from './geometry';
import {api_url} from './api';

class Diagnostic extends React.Component {
  constructor(props) {
     super(props);
     this.state = {
       section: "territory",
       status: "loading",
       error: null,
       geography: null,
       datasets: null
     };
   }

  setSection = (section) => {
      this.setState({
        section: section,
      })
      window.scrollTo(0, 0)
  }

  componentDidMount(){
    let myHeaders = new Headers()
    myHeaders.append("Accept", "application/json");
    myHeaders.append("Content-Type", "application/json");
    myHeaders.append("Access-Control-Allow-Origin", "*");
    myHeaders.append("Cache-Control", "max-age=604800");

    let init_datasets = [
      {endpoint: "general/geography", params: `?geo_codes=${this.props.geo_codes}`},
      {endpoint: "general/datasets", params: ""},
    ]

    Promise.all(
      init_datasets.map(d=> fetch(`${api_url}${d.endpoint}${d.params}`, {
            method: "GET",
            headers: myHeaders,
          }))
    ).then(results => Promise.all(results.map(r => r.json()))
    ).then((responses) => {
      this.setState({
        status: "loaded",
        geography: responses[0], //lists_to_objects(responses[0]),
        datasets: responses[1],
        geometry: computeGeometry(this.props.com_topo, responses[0], this.props.communes_attr, this.props.epci_attr)
      })
    }).catch((err) => {
      this.setState({
        status: "error",
        error: err.toString()
      });
    })
  }

  render() {
    let {geo_codes, name, zones, resetSelection, form_chart_active, setFormChart} = this.props;
    let {status, error, geography, geometry, datasets} = this.state;

    if(status === "loaded"){
      return(
        <div className="row">
          <div className="col">

            <Header name={name}/>

            <div className="row justify-content-center mb-5">
              <div className="col-11 col-md-11">
                <p onClick={resetSelection.bind(this)} style={{cursor: "pointer"}}><i>← retour à la sélection</i></p>
              </div>
            </div>

            <div className="row justify-content-center mb-5">
              <div className="col-11 col-md-11">

              <KeyFigures geography={geography}
                          geometry={geometry}
                          styles={this.props.styles}/>

              <Sections setSection={this.setSection} selectedSection={this.state.section} dev_mode={this.props.dev_mode}/>


              {this.state.section === "territory" ?
              <TerritoryProfile geography={geography}
                                geometry={geometry}
                                datasets={datasets}
                                setSection={this.setSection}
                                styles={this.props.styles}/>
              : this.state.section === "offer" ?
                <MobilityOffer geography={geography}
                                geometry={geometry}
                                datasets={datasets}
                                setSection={this.setSection}
                                styles={this.props.styles}/>
              : <MobilityProfile  geography={geography}
                                geometry={geometry}
                                datasets={datasets}
                                setSection={this.setSection}
                                styles={this.props.styles}/>
              }


              {<FormChart  link={this.props.form_banner_link} form_chart_active={form_chart_active} setFormChart={setFormChart}/>}

              {this.props.graphic_chart && <GraphicChart/>}

              {this.props.form_banner_link != null && <FormBanner link={this.props.form_banner_link} label={this.props.form_banner_label}/>}

              </div>
            </div>

            <Footer/>

          </div>
        </div>
      )
    }
    else if(status === "loading"){
      return(
        <div className="row">
          <div className="col">

            <Header/>

            <div className="row mt-5">
            </div>

            <div className="row justify-content-center mt-5">
              <div className="col-auto">
                <div class="spinner-grow" role="status">
                  <span class="sr-only">Loading...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    }
    else {
      return(
        <div className="row">
          <div className="col">

            <Header name={name}/>

            <div className="row justify-content-center mb-5">
              <div className="col-11 col-md-11">
                 <p>Une erreur est survenue. {error}.</p>
              </div>
            </div>

          </div>
        </div>
      )
    }
  }
}

export default Diagnostic;
