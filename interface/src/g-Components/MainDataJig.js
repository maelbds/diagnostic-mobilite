import React from 'react';

import MainJig from './MainJig';
import {YearsSet} from './YearsSet';

import * as topojson from "topojson";

import {api_url} from '../0-Home/api';

import {enrichGeojson} from '../f-Utilities/data_handling';

class MainDataJig extends React.Component {
  constructor(props) {
    super(props);
    let {geometry, geography, indicator_init} = this.props

    this.state = {
      status: "loading",
      error: null,

      meshesSet: indicator_init.meshesSet,
      selected_mesh: indicator_init.mesh_init,

      yearsSet: indicator_init.yearsSet,
      yearsSetUpdated: true,

      description: indicator_init.description,

      selected_ind: indicator_init,

      objects: this.formatObjects(geometry[indicator_init.mesh_init.type].mesh, [], indicator_init.mesh_init.type),
    }
  }

  updateMesh = (selected_mesh) => {
    this.setState({selected_mesh: selected_mesh})
  }

  updateYear = (name_year, selected_year) => {
    this.setState((prevState, prevProps) => {
      return {
        yearsSet: prevState.yearsSet.updateYear(name_year, selected_year),
        yearsSetUpdated: !prevState.yearsSetUpdated
      }
    })
  }

  updateIndicatorAndFilter = (indicator, filter, selection) => {
    if (selection !== null){
      this.props.filters.updateFilter[filter.name](this.props.filters.selected[filter.name], selection)
    }
    this.setState({selected_ind: indicator})
  }

  formatObjects = (geometry, responses, selected_mesh) => {
    let mesh_elements_responses = responses.filter(r => r.is_mesh_element).map(r => r.elements)

    let mesh_elements_geojson = geometry
    mesh_elements_responses.forEach((r) => {
      mesh_elements_geojson = enrichGeojson(mesh_elements_geojson, r)
    });

    let mesh_elements_ref = Object.assign(
      {},
      ...responses.filter(r => r.is_mesh_element).map(r => r.references),
    )
    let mesh_elements_leg = Object.assign(
      {},
      ...responses.filter(r => r.is_mesh_element).map(r => r.legend),
    )
    let sources = [].concat(
      ...responses.filter(r => "sources" in r).map(r => r.sources)
    )
    let not_mesh_elements = responses.filter(r => !r.is_mesh_element).map((r) => r.elements);

    let objects = Object.assign({
        mesh_elements_geojson: mesh_elements_geojson,
        mesh_elements_ref: mesh_elements_ref,
        mesh_elements_leg: mesh_elements_leg,
        sources: sources,
        perimeter: geometry.perimeter,
      }, ...not_mesh_elements
    )

    return objects
  }

  updateDatasets = (datasets, mesh, yearsSet) => {
      this.setState({
        status: "loading",
      })

      let myHeaders = new Headers()
      myHeaders.append("Accept", "application/json");
      myHeaders.append("Content-Type", "application/json");
      myHeaders.append("Access-Control-Allow-Origin", "*");
      myHeaders.append("Cache-Control", "max-age=604800");
      myHeaders.append("withCredentials", "true");
      let request_params = {method: "GET", headers: myHeaders};

      let com_codes = this.props.geography.com.map((c) => c.geo_code)
      let epci_codes = [...new Set(this.props.geography.com.map((c) => c.epci))]

      let codes = {
        com: com_codes,
        epci: epci_codes
      }

      const makeFetch = (dataset) => {
        let geo_codes_param = dataset.is_mesh_element ? `geo_codes=${codes[mesh].join(",")}` : `geo_codes=${com_codes.join(",")}`
        let mesh_param = `&mesh=${mesh}` // dataset.is_mesh_element ? `&mesh=${mesh}` : ""
        let concerned_year = yearsSet.getSelectedYearForDataset(dataset.name_api)
        let year_param =  concerned_year === null ? "" : `&year=${concerned_year}`

        return fetch(`${api_url}${dataset.name_api}?${geo_codes_param}${mesh_param}${year_param}`, request_params)
      }

      Promise.all(
        datasets.map(d=>makeFetch(d))
      ).then((responses) => {
        responses.forEach((response, i) => {
          if (response.status !== 200){ throw new Error(response.statusText); }
        });
        return Promise.all(responses.map(r => r.json()))
      }).then((responses) => {
        this.setState({
          status: "loaded",
          objects: this.formatObjects(this.props.geometry[mesh].mesh, responses, mesh)
        })
      }).catch((err) => {
        this.setState({
          status: "error",
          error: err.message
        });
      })
  }

  componentDidMount() {
    this.updateDatasets(this.state.selected_ind.datasets, this.state.selected_mesh.type, this.state.yearsSet)
  }

  componentDidUpdate(prevProps, prevState) {
    if(prevState.selected_ind !== this.state.selected_ind){
      let new_mesh = this.state.selected_ind.meshesSet.includesMesh(prevState.selected_mesh) ? prevState.selected_mesh : this.state.selected_ind.mesh_init;

      this.setState(() => {
        return {
        meshesSet: this.state.selected_ind.meshesSet,
        yearsSet: this.state.selected_ind.yearsSet,
        selected_mesh: new_mesh,
        description: this.state.selected_ind.description
      }})
      this.updateDatasets(this.state.selected_ind.datasets, new_mesh.type, this.state.selected_ind.yearsSet)
    }
    else if(prevState.selected_mesh !== this.state.selected_mesh |
            prevState.yearsSetUpdated !== this.state.yearsSetUpdated){
      this.updateDatasets(this.state.selected_ind.datasets, this.state.selected_mesh.type, this.state.yearsSet)
    }
  }

  render() {
    let {objects, status, error, meshesSet, selected_mesh, yearsSet, selected_ind, description} = this.state
    let {filters, map_id, indicators, title, geometry} = this.props

    let geo = {
      mesh_lines: geometry[selected_mesh.type].mesh_lines,
      mesh_outline: geometry[selected_mesh.type].mesh_outline,
      mesh: geometry[selected_mesh.type].mesh,
      perimeter: geometry.perimeter,
    }
    /*console.log("------")
    console.log(objects)
    console.log(geo)
    console.log(this.state)
    console.log(this.props)*/
    return(
              <MainJig  objects={objects}

                        status={status}
                        error={error}

                        selected_mesh={selected_mesh}
                        meshesSet={meshesSet}
                        updateMesh={this.updateMesh}

                        yearsSet={yearsSet}
                        updateYear={this.updateYear}

                        selected_ind={selected_ind}
                        indicators={indicators}
                        updateIndicatorAndFilter={this.updateIndicatorAndFilter}

                        filters={filters}

                        title={title}
                        description={description}
                        map_id={map_id}

                        styles={this.props.styles}
                        geo={geo}
                        />
    )
  }
}

export default MainDataJig;
