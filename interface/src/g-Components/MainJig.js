import React from 'react';

import CustomMap from '../i-Map/map';
import Info from '../f-Utilities/Info';
import Table from '../d-Table/Table';
import Loading from '../f-Utilities/Loading';
import DataSelectionButtonFilter from '../f-Utilities/DataSelectionButtonFilter';
import SelectMeshButton from '../f-Utilities/SelectMeshButton';
import SelectYearsButtons from '../f-Utilities/SelectYearsButtons';
import ViewButton from '../f-Utilities/ViewButton';
import DownloadButton from '../f-Utilities/DownloadButton';
import DownloadButtonLight from '../f-Utilities/DownloadButtonLight';
import SourcesRow from '../f-Utilities/SourcesRow';
import MapElement from '../i-Map/MapElement';
import {downloadMapImage} from '../i-Map/utilities';

import {downloadCSV, downloadGeoJson, initTable, objectsEquals} from '../f-Utilities/util_func';


class MainJig extends React.Component {
  getElementsMap(){
    let {objects, status, filters, selected_ind} = this.props;

    let layers = [], sources = [];

    if(status === "loaded" && this.all_indicators.map(k => k.indicator).includes(selected_ind.indicator)){
      ({layers, sources} = selected_ind.map_function(objects, filters.selected));
    }

    let sources_map = sources
    return {layers, sources_map}
  }

  getElementsTable(){
    let {objects, status, filters, selected_mesh, selected_ind} = this.props;
    let headlines, rows, align, format_table, format_csv, name_csv;

    if(status === "loaded" && this.all_indicators.map(k => k.indicator).includes(selected_ind.indicator)){
      ({headlines, rows, align, format_table, format_csv} = selected_ind.table_function(objects, filters.selected))
      name_csv = selected_ind.label
    } else {
      ({headlines, rows, align, format_table, format_csv} = initTable(objects))
      name_csv = "perimetre"
    }

    let sources_table = objects.sources
    return {headlines, rows, align, format_table, format_csv, sources_table, name_csv}
  }


  constructor(props) {
    super(props);
    let {indicators, selected_ind} = this.props

    this.all_indicators = indicators.map(i=>i.indicators).flat()

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

    this.props.indicators.map((ind) => ind.indicators).flat().forEach((ind) => {
      ind.updateDataSource(this.props.objects)
    });
  }

  componentDidUpdate(prevProps, prevState) {
    if(
      (prevProps.status === "loading" & this.props.status === "loaded") |
      (prevProps.status === "loaded" & this.props.status === "loading") |
      //(prevProps.selected_mesh !== this.props.selected_mesh) |
      //(prevProps.selected_ind !== this.props.selected_ind) |
      !objectsEquals(prevProps.filters.selected, this.props.filters.selected)
      ){
      this.setState(this.getElementsMap())
      this.setState(this.getElementsTable())

      this.props.indicators.map((ind) => ind.indicators).flat().forEach((ind) => {
        ind.updateDataSource(this.props.objects)
      });
    }

    if(prevState.layers !== this.state.layers){
      this.custom_map.updateLayers(this.state.layers)
    }
    if(prevProps.selected_mesh !== this.props.selected_mesh){
      this.custom_map.updateMesh({mesh: this.props.selected_mesh.type, geo: this.props.geo})
    }

  }

  componentWillUnmount(){
    this.custom_map.endMap()
  }

  render() {
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

                  {this.props.indicators.map((item, j)=>
                    <div>
                      {item.name !== null &&
                        <div className="row mt-4">
                          <div className="col-12">
                            <p className="mb-1"><i>{item.name}</i></p>
                          </div>
                        </div>}

                        {item.indicators.map((d, i)=>
                          <DataSelectionButtonFilter  ind={d} selected_indicator={this.props.selected_ind.indicator} key={`${i}-${j}`}
                                                      selected_filters={this.props.filters.selected}
                                                      updateIndicatorAndFilter={this.props.updateIndicatorAndFilter} />
                        )}
                    </div>
                  )}
                  </div>

                  {this.props.description !== undefined && this.props.description !==null &&
                    <div className="col-6 col-lg-12 mt-0 mt-lg-4">
                      <p className="mb-1">{this.props.description}</p>
                    </div>}

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
                           error={this.props.error}/>
                  }
                </div>

                <div className="col-12" style={{display: this.state.viewMap ? "block" : "none"}}>
                  <MapElement id={this.props.map_id}/>
                  <SourcesRow selected_sources={this.state.sources_map}/>

                </div>

                <div className="col-12" style={{display: this.state.viewTable ? "block" : "none"}}>
                   <Table headlines={this.state.headlines}
                          rows={this.state.rows}
                          align={this.state.align}
                          format={this.state.format_table}/>
                    <SourcesRow selected_sources={this.state.sources_table}/>
                </div>
              </div>

              <div className="row mt-3 align-items-top justify-content-between">
                <div className="col-auto">
                  <div className="row">
                      <ViewButton active={this.state.viewMap} label="Carte" setView={this.setView.bind(this, "map")} />
                      <ViewButton active={this.state.viewTable} label="Tableau" setView={this.setView.bind(this, "table")} />
                  </div>
                </div>
                <div className="col-auto">
                  <div className="row">
                      <DownloadButtonLight onClick={downloadMapImage.bind(this, this.state.custom_map.map, this.props.selected_ind.label)}
                                           title="Télécharger la carte au format PNG (image)"
                                           label="carte / .png"/>
                      <DownloadButtonLight onClick={downloadCSV.bind(this, this.state.headlines, this.state.rows, this.state.format_csv, this.state.name_csv)}
                                           title="Télécharger les données au format CSV (tableau)"
                                           label="tableau / .csv"/>
                  </div>
                </div>

                {/*<DownloadButton download={downloadMapImage.bind(this, this.state.custom_map.map, this.props.selected_ind.label)}
                                label={"Télécharger la carte au format PNG"}/>
                <DownloadButton download={downloadCSV.bind(this, this.state.headlines, this.state.rows, this.state.format_csv, this.state.name_csv)} />

                <DownloadButton download={downloadGeoJson.bind(this, this.props.objects.mesh_geojson, this.props.selected_ind.label)}
                                label={"Télécharger la carte au format GeoJson"}/>*/}
              </div>

          </div>
        </div>
    )
  }
}

export default MainJig;
