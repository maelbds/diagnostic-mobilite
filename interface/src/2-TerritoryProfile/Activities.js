import React, { Component } from 'react';

import getMyMap from '../b-LeafletMap/leaflet_map';
import {createCommunesNamesLayerEasy} from '../b-LeafletMap/LeafletMapElement/createCommuneName';
import {getEducationElements} from './education';
import {getHealthElements} from './health';
import {getFoodShopElements} from './food_shop';
import {getGeneralElements} from './general';

import LeafletMapLegend from '../b-LeafletMap/LeafletMapLegend';
import Info from '../f-Utilities/Info';
import SourcesRow from '../f-Utilities/SourcesRow';
import DataSelectionButton from '../f-Utilities/DataSelectionButton';

import {c_missing_data, c_gradient_greens, c_gradient_reds_greens, c_yellow} from '../a-Graphic/Colors';
import {formatFigure, downloadCSV, cols_to_rows} from '../f-Utilities/util_func';

class Activities extends React.Component {
  getCommunesMap(selected){
    /* COMMUNES */
    let communes = this.props.territory.communes;
    let communes_coords = communes.map((c) => c.center);
    let communes_names = communes.map((c) => c.name);

    if(selected == "education"){
      var {layer_to_fit, layers, legend, sources} = getEducationElements(communes, this.props.territory.places)
    }
    else if(selected == "health"){
      var {layer_to_fit, layers, legend, sources} = getHealthElements(communes, this.props.territory.places)
    }
    else if(selected == "food"){
      var {layer_to_fit, layers, legend, sources} = getFoodShopElements(communes, this.props.territory.places)
    }
    else if(selected == "general"){
      var {layer_to_fit, layers, legend, sources} = getGeneralElements(communes, this.props.territory.activity_cluster)
    }
    layers.push(createCommunesNamesLayerEasy(communes))

    return {selected, layer_to_fit, layers, legend, sources}
  }

  constructor(props) {
    super(props);
    let selected_init = "education"

    this.state = Object.assign({}, {
      name_csv: "population_densite",
    },this.getCommunesMap(selected_init));
  }

  displayCategory = (selected) => {
      this.setState(this.getCommunesMap(selected))
  }

  componentDidMount() {
    // --- init map
    let mymap = this.mymap = getMyMap("activities_map", true, 0.3);
    // --- add layers
    this.state.layers.map((layer)=>layer.addTo(mymap))
    // --- center the map
    mymap.fitBounds(this.state.layer_to_fit.getBounds());
  }

  componentDidUpdate(prevProps, prevState) {
    // --- update
    prevState.layers.map((layer)=>this.mymap.removeLayer(layer))
    this.state.layers.map((layer)=>layer.addTo(this.mymap))
  }

  render() {
    let data_list = [{selected: "education", label: "éducation"},
                     {selected: "health", label: "santé"},
                     {selected: "food", label: "commerces alimentaires"},
                     {selected: "general", label: "pôles de commerces et services"}]

    return(
          <div className="row content mt-4 mb-5">

            <div className="col-3">
                <div className="row">
                  <div className="col-12">
                    <h3 className="mb-3">activités</h3>
                  </div>
                </div>

                <div className="row">
                  <div className="col-12 line-border">
                    {data_list.map((d)=>
                      <DataSelectionButton selected={this.state.selected === d.selected}
                                           display_category={this.displayCategory.bind(this, d.selected)} label={d.label} />
                    )}
                  </div>
                </div>
            </div>

            <div className="col-9">
              <div className="row">
                <div className="col-12">
                <LeafletMapLegend legend={this.state.legend}
                                  all_sources={this.props.territory.sources}
                                  concerned_sources={this.state.sources}
                                  id="activities_map"
                                  height="500px"/>
                </div>
              </div>


          </div>
        </div>
    )
  }
}

export default Activities;
