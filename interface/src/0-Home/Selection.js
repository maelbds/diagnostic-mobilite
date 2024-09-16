import React, { Component } from 'react';
import * as d3 from "d3";

import Header from '../f-Utilities/Header';
import Footer from '../f-Utilities/Footer';
import SelectionMap from '../5-Selection/SelectionMap2';
import SelectedMap from '../5-Selection/SelectedMap';
import SelectedTerritory from '../5-Selection/SelectedTerritory';

import FormBanner from '../f-Utilities/FormBanner'


class Selection extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selected_communes: [],
      selected_zones: [],
      sources: {
        "map": {label: "Admin Express COG CARTO (IGN 2023)",
                link: "https://geoservices.ign.fr/adminexpress"},
        "trait": {label: "Traitement d'après Icem7",
                link: "https://www.icem7.fr/cartographie/un-fond-de-carte-france-par-commune-optimise-pour-le-web-et-lanalyse-statistique/"},
        "aav": {label: "Aires d'attraction des villes 2020 (INSEE 2023)",
                link: "https://www.insee.fr/fr/information/4803954"},
        "epci": {label: "Code officiel géographique (INSEE 2023)",
                link: "https://www.insee.fr/fr/information/6800675"},
      },
    };
    this.updateSelectedCommunes = this.updateSelectedCommunes.bind(this);
    this.updateSelectedZones = this.updateSelectedZones.bind(this);
  }

  updateSelectedCommunes(new_selected_communes){
    let max_communes_nb = 400
    if (new_selected_communes.length > max_communes_nb){
      alert(`La sélection est limitée à ${max_communes_nb} communes pour le moment. Cela sera augmenté par la suite.`)
      this.setState({selected_communes: new_selected_communes.slice(0, max_communes_nb)})
    } else {
      this.setState({selected_communes: new_selected_communes})
    }
  }

  updateSelectedZones(new_zones){
    this.setState({selected_zones: new_zones})
  }

  render() {
    const {selected} = this.state;

    return(

  <div className="row">
    <div className="col">

      <Header/>

      <div className="row justify-content-center mt-5">
        <div className="col-11 col-md-11">

          <SelectionMap id="selection_map"
                        data_selection_map={this.props.data_selection_map}
                        sources={this.state.sources}
                        selected_communes={this.state.selected_communes}
                        updateSelectedCommunes={this.updateSelectedCommunes}

                        loadTerritory={this.props.loadTerritory}
                        />

            <div className="row mt-5 mb-5"></div>

            {/*<SelectedMap id="selected_map"
                         data={this.state.data_full}
                         communes={this.state.communes}
                         d_communes={this.state.d_communes}
                         epci={this.state.epci}
                         aav={this.state.aav}
                         with_emd={this.state.with_emd}
                         selected_communes={this.state.selected_communes}
                         updateSelectedZones={this.updateSelectedZones}/>

              <div className="row mt-5 mb-5"></div>

              <SelectedTerritory id="selected_territory"
                                 communes={this.state.communes}
                                 epci={this.state.epci}
                                 d_communes={this.state.d_communes}
                                 selected_communes={this.state.selected_communes}
                                 selected_zones={this.state.selected_zones}
                                 loadTerritory={this.props.loadTerritory}/>*/}


               <FormBanner link={this.props.form_banner_link} label={this.props.form_banner_label}/>

          </div>
        </div>

        <Footer/>
      </div>
    </div>
    )
  }
}

export default Selection;
