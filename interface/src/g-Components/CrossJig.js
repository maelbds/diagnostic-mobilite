import React from 'react';

import CustomMap from '../i-Map/map';
import Info from '../f-Utilities/Info';
import Table from '../d-Table/Table';
import Loading from '../f-Utilities/Loading';
import DataSelectionButtonFilterRadio from '../f-Utilities/DataSelectionButtonFilterRadio';
import DataSelectionButtonFilterCheckbox from '../f-Utilities/DataSelectionButtonFilterCheckbox';
import SelectMeshButton from '../f-Utilities/SelectMeshButton';
import SelectYearsButtons from '../f-Utilities/SelectYearsButtons';
import ViewButton from '../f-Utilities/ViewButton';
import DownloadButton from '../f-Utilities/DownloadButton';
import SourcesRow from '../f-Utilities/SourcesRow';
import {ChoroLayer} from '../i-Map/Layers/ChoroLayer'
import {CircleLayer} from '../i-Map/Layers/CircleLayer'

import MapElement from '../i-Map/MapElement';
import {downloadMapImage} from '../i-Map/utilities';

import {c_gradient_greens, c_yellow} from '../a-Graphic/Colors';

import {downloadCSV, downloadGeoJson, initMap, initTable, formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import * as topojson from "topojson";


class CrossJig extends React.Component {
  getElementsMap(){
    let {objects, status, filters, selected_ind} = this.props;

    let layers = [], sources = [];

    if(status === "loaded"){
      selected_ind.choropleth.forEach((ind) => {
        layers = layers.concat(ind.layers.choropleth(objects, filters.selected))
      });
      selected_ind.circle.forEach((ind) => {
        layers = layers.concat(ind.layers.circle(objects, filters.selected))
      });
      selected_ind.path.forEach((ind) => {
        layers = layers.concat(ind.layers.path(objects, filters.selected))
      });
      sources = objects.sources
    }

    let sources_map = sources
    return {layers, sources_map}
  }

  getElementsTable(){
    let {objects, status, filters, selected_mesh, selected_ind} = this.props;
    let all_headlines = [], all_cols = [], all_rows = [], all_format_table = [], all_format_csv = [], all_align = [];
    let headlines = [], cols = [], rows = [], format_table = [], format_csv = [], align = [];

    if(status === "loaded"){
      let mesh_elements = objects.mesh_elements_geojson.features.map((f) => f.properties);
      let all_selected_indicators = Object.values(selected_ind).flat()
      let unique_selected_indicators = all_selected_indicators.filter((ind, i) => all_selected_indicators.map((f) => f.indicator).indexOf(ind.indicator) === i)

      unique_selected_indicators.forEach((ind) => {
        if("mesh" in ind.tables){
          ({headlines, cols, format_table, format_csv, align} = ind.tables.mesh(objects, filters.selected))
          all_headlines = all_headlines.concat(headlines)
          all_cols = all_cols.concat(cols)
          all_format_table = all_format_table.concat(format_table)
          all_format_csv = all_format_csv.concat(format_csv)
          all_align = all_align.concat(align)
        }
      });

      headlines = ["Code INSEE", "Nom"].concat(all_headlines)
      cols = [mesh_elements.map((c)=> c.geo_code), mesh_elements.map((c)=> c.name)].concat(all_cols)
      format_table = [(f)=>f, (f)=>f].concat(all_format_table)
      format_csv = [(f)=>f, (f)=>f].concat(all_format_csv)
      align = ["l", "l"].concat(all_align)

      rows = cols_to_rows(cols).sort((a, b)=> ('' + a[1]).localeCompare(b[1])) // tri par ordre alphabétique des noms
    } else {
      ({headlines, rows, align, format_table, format_csv} = initTable(objects))
    }

    let sources_table = objects.sources
    let name_csv = "à la carte"
    return {headlines, rows, align, format_table, format_csv, sources_table, name_csv}
  }


  constructor(props) {
    super(props);
    let {indicators, selected_ind} = this.props

    this.all_indicators = indicators

    this.state = Object.assign({}, {
      viewMap: true,
      viewTable: false,
      custom_map: {map: null},
    },
    this.getElementsMap(),
    this.getElementsTable());
  }

  setView = (view) => {
      this.setState({
        viewMap: view === "map",
        viewTable: view === "table",
      })
  }

  componentDidMount(){
    let custom_map = this.custom_map = new CustomMap(this.props.map_id, this.props.styles, this.props.geo)
    this.setState({custom_map: custom_map})
  }

  componentDidUpdate(prevProps, prevState) {
    console.log(this.state.layers)
    if(
      (prevProps.status === "loading" & this.props.status === "loaded") |
      (prevProps.status === "loaded" & this.props.status === "loading") |
      //(prevProps.selected_mesh !== this.props.selected_mesh) |
      //(prevProps.selected_ind !== this.props.selected_ind) |
      (prevProps.filters.selected !== this.props.filters.selected)
      ){
      this.setState(this.getElementsMap())
      this.setState(this.getElementsTable())
    }

    if(prevState.layers !== this.state.layers){
      this.custom_map.updateLayers(this.state.layers)
    }
    if(prevProps.selected_mesh !== this.props.selected_mesh){
      this.custom_map.updateMesh({mesh: this.props.selected_mesh.type, geo: this.props.geo})
    }

  }

  render() {
    let choropleth_indicators = this.props.indicators.filter((ind) => "choropleth" in ind.layers)
    let circle_indicators = this.props.indicators.filter((ind) => "circle" in ind.layers)
    let path_indicators = this.props.indicators.filter((ind) => "path" in ind.layers)

    return(
          <div className="row content mt-4 mb-5">

            <div className="col-12 col-lg-3 mb-3 mb-lg-0">
                <div className="row">
                  <div className="col-12">
                    <h3 className="mb-3">{this.props.title}</h3>
                  </div>
                </div>

                <div className="row justify-content-between">
                  <div className="col-5 col-lg-12 line-border">


                    <div className="row">
                      <div className="col-12">
                        <p><i>Applats de couleurs :</i></p>
                      </div>
                    </div>

                    {choropleth_indicators.map((d, i)=>
                      <DataSelectionButtonFilterRadio  ind={d} selected_indicator={this.props.selected_ind.choropleth} key={`${i}`}
                                                  selected_filters={this.props.filters.selected}
                                                  type={"choropleth"}
                                                  updateIndicatorAndFilter={this.props.updateIndicatorAndFilter} />
                    )}


                    <div className="row mt-4">
                      <div className="col-12">
                        <p><i>Cercles :</i></p>
                      </div>
                    </div>

                    {circle_indicators.map((d, i)=>
                      <DataSelectionButtonFilterRadio  ind={d} selected_indicator={this.props.selected_ind.circle} key={`${i}`}
                                                  selected_filters={this.props.filters.selected}
                                                  type={"circle"}
                                                  updateIndicatorAndFilter={this.props.updateIndicatorAndFilter} />
                    )}


                    <div className="row mt-4">
                      <div className="col-12">
                        <p><i>Tracés :</i></p>
                      </div>
                    </div>

                    {path_indicators.map((d, i)=>
                      <DataSelectionButtonFilterCheckbox  ind={d} selected_indicator={this.props.selected_ind.path} key={`${i}`}
                                                  selected_filters={this.props.filters.selected}
                                                  type={"path"}
                                                  updateIndicatorAndFilter={this.props.updateIndicatorAndFilter} />
                    )}

                  </div>

                </div>
            </div>

            <div className="col-12 col-lg-9">
              <div className="row mb-3">
                <SelectMeshButton selected_mesh={this.props.selected_mesh} meshesSet={this.props.meshesSet} updateMesh={this.props.updateMesh}/>

                <SelectYearsButtons yearsSet={this.props.yearsSet} updateYear={this.props.updateYear}/>
              </div>


              <div className="row">
                <div className="col-12" style={{position: "absolute", zIndex: 3000}}>
                  {this.props.status !== "loaded" &&
                  <Loading loading={this.props.status === "loading"}
                           error={this.props.error}
                            height="750px"
                            />
                  }
                </div>

                <div className="col-12" style={{display: this.state.viewMap ? "block" : "none"}}>
                  <MapElement id={this.props.map_id} height="750px"/>
                  <SourcesRow selected_sources={this.state.sources_map}/>

                </div>

                <div className="col-12" style={{display: this.state.viewTable ? "block" : "none"}}>
                   <Table headlines={this.state.headlines}
                          rows={this.state.rows}
                          align={this.state.align}
                          height="750px"
                          format={this.state.format_table}/>
                    <SourcesRow selected_sources={this.state.sources_table}/>
                </div>
              </div>

              <div className="row mt-3">
                <ViewButton active={this.state.viewMap} label="Carte" setView={this.setView.bind(this, "map")} />
                <ViewButton active={this.state.viewTable} label="Tableau" setView={this.setView.bind(this, "table")} />

                <DownloadButton download={downloadMapImage.bind(this, this.state.custom_map.map, "a la carte")}
                                label={"Télécharger la carte au format PNG"}/>
                <DownloadButton download={downloadCSV.bind(this, this.state.headlines, this.state.rows, this.state.format_csv, this.state.name_csv)} />
                {/*<DownloadButton download={downloadGeoJson.bind(this, this.props.objects.mesh_geojson, this.props.selected_ind.label)}
                                label={"Télécharger la carte au format GeoJson"}/>*/}
              </div>

          </div>
        </div>
    )
  }
}

export default CrossJig;
