import React, { Component } from 'react';
import * as d3 from "d3";

import Header from '../f-Utilities/Header';
import SelectionMap from '../5-Selection/SelectionMap';
import SelectedMap from '../5-Selection/SelectedMap';
import SelectedTerritory from '../5-Selection/SelectedTerritory';

import FormBanner from '../f-Utilities/FormBanner'


class Selection extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selected_communes: [],
      selected_zones: [],
      error: null,
      isLoaded: false,
      sources: {
        "map": {label: "Contour simplifié des communes de France (traitement icem7 d'après IGN 2022)",
                link: "https://www.data.gouv.fr/fr/datasets/contours-des-communes-de-france-simplifie-avec-regions-et-departement-doutre-mer-rapproches/"},
        "aav": {label: "Aires d'attraction des villes 2020 (INSEE 2022)",
                link: "https://www.insee.fr/fr/information/4803954"},
        "epci": {label: "Communes et EPCI selon COG (INSEE 2022)",
                link: "https://www.insee.fr/fr/information/6051727"},
      }
    };
    this.updateSelectedCommunes = this.updateSelectedCommunes.bind(this);
    this.updateSelectedZones = this.updateSelectedZones.bind(this);
  }

  updateSelectedCommunes(new_selected_communes){
    this.setState({selected_communes: new_selected_communes})
  }

  updateSelectedZones(new_zones){
    this.setState({selected_zones: new_zones})
  }

  componentDidMount(){
    Promise.all([
        d3.json("selection-geo-a-com2022-topo-2154-ultralight-with-epci.json"),
        d3.json("selection-communes.json"),
        d3.json("selection-epci.json"),
        d3.json("selection-aav.json"),
        d3.json("selection-geo-a-com2022-topo-2154.json"),
    ]).then((files) => {
        const data_light = files[0]
        const communes = files[1]
        const epci = files[2]
        const aav = files[3]
        const data_full = files[4]
        let with_emd = ['34005', '34010', '34011', '34012', '34013', '34014', '34016', '34022', '34023', '34024', '34027',
        '34029', '34033', '34035', '34036', '34039', '34041', '34042', '34043', '34045', '34047', '34048', '34050', '34051',
        '34057', '34058', '34060', '34064', '34066', '34067', '34076', '34077', '34078', '34079', '34082', '34087', '34088',
        '34090', '34095', '34102', '34103', '34106', '34108', '34110', '34111', '34113', '34114', '34115', '34116', '34118',
        '34120', '34122', '34123', '34124', '34125', '34127', '34128', '34129', '34131', '34133', '34134', '34137', '34138',
        '34142', '34143', '34145', '34146', '34150', '34151', '34152', '34153', '34154', '34156', '34157', '34159', '34163',
        '34164', '34165', '34169', '34171', '34172', '34173', '34174', '34176', '34177', '34179', '34180', '34185', '34188',
        '34192', '34194', '34195', '34197', '34198', '34202', '34204', '34205', '34208', '34210', '34212', '34213', '34215',
        '34217', '34220', '34221', '34222', '34227', '34233', '34239', '34240', '34241', '34242', '34243', '34244', '34246',
        '34247', '34248', '34249', '34251', '34254', '34255', '34256', '34259', '34261', '34262', '34263', '34264', '34265',
        '34266', '34267', '34268', '34270', '34272', '34274', '34276', '34277', '34280', '34281', '34282', '34283', '34286',
        '34287', '34288', '34290', '34292', '34294', '34295', '34296', '34297', '34301', '34303', '34304', '34306', '34307',
        '34309', '34313', '34314', '34316', '34317', '34318', '34320', '34321', '34322', '34323', '34327', '34328', '34333',
        '34337', '34340', '34341', '34342', '34343', '34344'] // EDGT Montpellier communes

        const d_communes = new Map(data_light.objects.a_com2022.geometries.map((c)=> [c.properties.codgeo, c.properties.libgeo]))

        this.setState({
          isLoaded: true,
          data_light,
          data_full,
          communes,
          epci,
          aav,
          with_emd,
          d_communes
        });

    }).catch((err) => {
        console.log(err)
          this.setState({
            isLoaded: true,
            error: err
          });
    })
  }

  render() {
    const {error, isLoaded, selected} = this.state;
    return(

  <div className="row">
    <div className="col">

      <Header/>

      <div className="row justify-content-center">
        <div className="col-11 col-md-11">



            {
            error ?     <div>Erreur : {error.message}</div> :
            !isLoaded ? <div><p>Chargement…</p></div> :
                        <div>

                        <SelectionMap id="selection_map"
                                      data={this.state.data_light}
                                      communes={this.state.communes}
                                      epci={this.state.epci}
                                      aav={this.state.aav}
                                      with_emd={this.state.with_emd}
                                      sources={this.state.sources}
                                      updateSelectedCommunes={this.updateSelectedCommunes}/>

                        <div className="row mt-5 mb-5"></div>

                        <SelectedMap id="selected_map"
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
                                             loadTerritory={this.props.loadTerritory}/>

                           <div className="row mt-5 mb-5"></div>

                           <FormBanner link="https://forms.gle/KkWyGsG7ubLRaoWq6"/>

                          </div>
            }
        </div>
      </div>
    </div>
  </div>
    )
  }
}

export default Selection;
