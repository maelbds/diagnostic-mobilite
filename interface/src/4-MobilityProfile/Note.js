import React from 'react';
import * as d3 from "d3";

import Disclaimer from '../f-Utilities/Disclaimer';
import Banner from '../f-Utilities/Banner';

import {api_call} from '../0-Home/api';
import {c_yellow, c_orange, c_blue} from '../a-Graphic/Colors';


class Note extends React.Component {
  constructor(props){
    super(props)

    this.state = {
      id: "modes_chart",
      name_file: "parts_modales",
      status: "loading",
      data: {
        origin: null,
      },
    }
  }

  componentDidMount(){
    let endpoints = ["mobility/origin"]
    api_call.call(this, endpoints)
  }

  render(){
    let origin = this.state.data.origin;

    if (this.state.status === "error") {
      return (
        <p>Erreur...</p>
      )
    }
    else{
      return(
        <div className="row">
          <div className="col-12">

          {origin === "model" && <Disclaimer/> }
          {origin === "emd" && <Banner color={c_yellow} message={"Les données qui suivent sont issues d'une enquête mobilité locale. L'éventuelle mention \"imprécis\" indique que le territoire sélectionné présente un échantillon trop restreint pour afficher davantage de détails."}/> }
          {origin === "emd_and_model" && <Banner color={c_orange} message="Le territoire sélectionné est à cheval entre deux zones qui ont des modalités différentes de calcul des pratiques de mobilité. Veuillez sélectionner un territoire entièrement couvert par une enquête mobilité locale, ou entièrement en dehors de ces enquêtes."/> }
          {origin === "not_covered" && <Banner color={c_orange} message="Le territoire sélectionné n'est pas couvert par les données de pratiques de déplacement."/> }
          {origin === "emd_not_added" && <Banner color={c_blue} message="Le territoire sélectionné est couvert par une enquête mobilité locale mais elle n'a pas été ajoutée à Diagnostic Mobilité. Veuillez vous rapprocher de la collectivité locale afin de demander son intégration."/> }

          </div>
        </div>
      );
    }
  }
}

export default Note;
