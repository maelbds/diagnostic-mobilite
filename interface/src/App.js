import React, { Component } from 'react';

import Selection from './0-Home/Selection';
import Diagnostic from './0-Home/Diagnostic';


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      manual_mode: true, // if false, display selection page first, if true, display directly visualisation page of given json below
      file_if_manual_mode: "territory-demo_manual_mode.json", // name of territory file to display, located into public folder
      dev_mode: false, // to display a fourth section "dev", usefull to try new indicators
      graphic_chart: false, // to display the graphic chart at the end of the visualisation page
      form_banner_link_visualisation: "https://forms.gle/ZKigEuXA26gLLZTs6", // to display a fixed banner at the end of the page with link to form
      step: "selection",
      error: null,
      isLoaded: false,
      selected: false,
      territory: null
    };
  }

  // this function is used when manual_mode is false. We triger it from selection page we given info about the studied territory
  loadTerritory = (title, geo_codes, zones) => {
    let myHeaders = new Headers()
    myHeaders.append("Accept", "application/json");
    myHeaders.append("Content-Type", "application/json");
    myHeaders.append("Access-Control-Allow-Origin", "*");

    let bodyRequest = JSON.stringify({
      title: title,
      geo_codes: geo_codes,
      zones: zones
    })


    this.setState({
      step: "loading"
    })

    // here we send request to server with given info about our territory
    fetch("http://127.0.0.1:5000/territory",
        {
          method: "POST",
          headers: myHeaders,
          body: bodyRequest,
        }
     ).then(res => res.json()) // once request response received, we change state, which enables visualisation page display
      .then(
        (result) => {
          console.log(result)
          this.setState({
            territory: result,
            step: "diagnostic_loaded"
          })
        },
        (error) => {
          this.setState({
            error: error,
            step: "error"
          })
        }
      )
  }

  // this function is used when manual_mode is true. We directly ask for saved json
  componentDidMount() {
    fetch(this.state.file_if_manual_mode)
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            isLoaded: true,
            territory: result
          });
        },
        (error) => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      )
  }

  render() {
    const {manual_mode, dev_mode, graphic_chart, form_banner_link_visualisation, step, error, isLoaded, selected, territory } = this.state;
    if (manual_mode){
      if (error) {
        return <div>Erreur : {error.message}</div>;
      } else if (!isLoaded) {
        return <div><p>Chargement…</p></div>;
      } else {
        return (
          <Diagnostic territory={territory} dev_mode={dev_mode} graphic_chart={graphic_chart} form_banner_link={form_banner_link_visualisation}/>
        );
      }
    }
    else{
      if (step == "selection") return <Selection loadTerritory={this.loadTerritory}/>
      else if (step =="loading") return <div><p>Chargement et calcul des données du territoire d'étude…</p></div>
      else if (step =="diagnostic_loaded") return <Diagnostic territory={territory}  dev_mode={dev_mode}/>
      else return <div>Une erreur est survenue… ({error})</div>
    }
  }
}

export default App;
