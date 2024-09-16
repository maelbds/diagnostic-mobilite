import React from 'react';

import CrossJig from './CrossJig';
import {YearsSet} from './YearsSet';
import {intersectMeshesSet} from './MeshesSet';

import {api_url} from '../0-Home/api';

import * as topojson from "topojson";

import {enrichGeojson, drop_duplicates_sources} from '../f-Utilities/data_handling';

class CrossDataJig extends React.Component {
  constructor(props) {
    super(props);
    let {geometry, geography, indicator_init} = this.props

    let all_indicators = Object.values(indicator_init).flat()
    // required datasets
    let all_datasets = [].concat(all_indicators.map((i) => i.datasets)).flat()
    // years union
    let all_years_set = [].concat(all_indicators.map((i) => i.yearsSet.years)).flat()
    let yearsSetAll = new YearsSet(all_years_set)
    // meshes intersection
    let meshesSet = intersectMeshesSet(all_indicators.map((i) => i.meshesSet))
    console.log(meshesSet)

    this.state = {
      status: "loading",
      error: null,

      meshesSet: meshesSet, //{com: "Communes", epci: "EPCI"}, // indicator_init.choropleth.meshes,
      selected_mesh: meshesSet.getMeshInit(), // indicator_init.choropleth.mesh_init,

      yearsSet: yearsSetAll,
      yearsSetUpdated: true,

      selected_ind: indicator_init,

      objects: this.formatObjects(geometry[meshesSet.getMeshInit().type].mesh, [], meshesSet.getMeshInit().type),
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

  updateIndicatorAndFilter = (type, indicator, filter, selection) => {
    if (selection !== null){
      this.props.filters.updateFilter[filter.name](this.props.filters.selected[filter.name], selection)
    } else {
      if(type === "choropleth" | type === "circle"){
        this.setState((prevState, prevProps) => ({
          selected_ind: {...prevState.selected_ind, ...{[type]: [indicator]}}
        }))
      } else if(type === "path"){
        this.setState((prevState, prevProps) => {
          let prev_path_ind = prevState.selected_ind.path
          let new_path_ind
          if(prev_path_ind.map((i) => i.indicator).includes(indicator.indicator)){
            new_path_ind = prev_path_ind.filter((i) => i.indicator !== indicator.indicator)
          } else {
            new_path_ind = prev_path_ind.concat([indicator])
          }
          return {
            selected_ind: {...prevState.selected_ind, ...{[type]: new_path_ind}}
          }
        })
      }
    }
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
        sources: drop_duplicates_sources(sources),
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
      let request_params = {method: "GET", headers: myHeaders};

      let com_codes = this.props.geography.com.map((c) => c.geo_code)
      let epci_codes = [...new Set(this.props.geography.com.map((c) => c.epci))]

      let codes = {
        com: com_codes,
        epci: epci_codes
      }

      const makeFetch = (dataset, i) => {
        let geo_codes_param = dataset.is_mesh_element ? `geo_codes=${codes[mesh].join(",")}` : `geo_codes=${com_codes.join(",")}`
        let mesh_param = dataset.is_mesh_element ? `&mesh=${mesh}` : ""
        console.log(yearsSet)
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
    let all_datasets = [].concat(Object.values(this.state.selected_ind)).flat().map((i) => i.datasets).flat()
    /*let all_years_set = [].concat(Object.values(this.state.selected_ind)).flat().map((i) => i.yearsSet.years).flat()
    let yearsSetAll = new YearsSet(all_years_set)
    console.log(all_years_set)*/
    this.updateDatasets(all_datasets, this.state.selected_mesh.type, this.state.yearsSet)
  }

  componentDidUpdate(prevProps, prevState) {
    let all_datasets = [].concat(Object.values(this.state.selected_ind)).flat().map((i) => i.datasets).flat()

    let all_years_set = [].concat(Object.values(this.state.selected_ind)).flat().map((i) => i.yearsSet.years).flat()
    let yearsSetAll = new YearsSet(all_years_set)

    if(prevState.selected_ind !== this.state.selected_ind){

      let all_indicators = Object.values(this.state.selected_ind).flat()
      let meshesSet = intersectMeshesSet(all_indicators.map((i) => i.meshesSet))
      let new_mesh = meshesSet.getMeshInit() //prevState.selected_mesh in this.state.selected_ind.meshes ? prevState.selected_mesh : this.state.selected_ind.mesh_init;

      this.setState(() => {
        return {
        meshesSet: meshesSet, // {com: "Communes", epci: "EPCI"},// this.state.selected_ind.meshes,
        yearsSet: yearsSetAll,
        selected_mesh: new_mesh,
        description: this.state.selected_ind.description
      }})
      this.updateDatasets(all_datasets, new_mesh.type, yearsSetAll)
    }
    else if(prevState.selected_mesh !== this.state.selected_mesh |
            prevState.yearsSetUpdated !== this.state.yearsSetUpdated){
      this.updateDatasets(all_datasets, this.state.selected_mesh.type, yearsSetAll)
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


    return(
              <CrossJig  objects={objects}

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

export default CrossDataJig;
