import {Year} from './Year';
import {YearsSet} from './YearsSet';

import {createMeshesSetFromTypes, intersectMeshesSet} from './MeshesSet'

import {cols_to_rows} from '../f-Utilities/util_func';


export const Indicator = class {
  constructor(args){
    this.indicator = args.indicator
    this.label = args.label
    this.label_i = "label_i" in args ? args.label_i : null
    this.legend = "legend" in args ? args.legend : null
    this.description = "description" in args ? args.description : null

    this.data_source = "data_source" in args ? args.data_source : "verified"
    this.data_source_from_request = "data_source_from_request" in args ? args.data_source_from_request : false
    this.data_source_function = "data_source_function" in args ? args.data_source_function : false

    /*this.sources_names = args.sources_names*/

    /*this.meshes = "meshes" in args ? args.meshes
    this.mesh_init = "mesh_init" in args ? args.mesh_init : "com"*/

    /*this.years = "years" in args ? args.years : {}
    this.year_init = "year_init" in args ? args.year_init : null*/

    this.filters = "filters" in args ? args.filters : []

    this.map_function = this.layer_map
    this.table_function = this.table
    this.updateDataSource = this.updateDataSource
    this.layers = args.layers
    this.tables = args.tables

    this.datasets_names = "datasets_names" in args ? args.datasets_names : []
  }


  layer_map(objects, selected_filters=null){
    let {sources} = objects

    let layers = Object.values(this.layers).map((layer_func) => layer_func(objects, selected_filters))
    layers = [].concat(layers).flat()

    return {layers, sources}
  }

  table(objects, selected_filters=null){
    if ("mesh" in this.tables){
      let mesh_elements = objects.mesh_elements_geojson.features.map((f) => f.properties);
      let {headlines, cols, format_table, format_csv, align} = this.tables.mesh(objects, selected_filters)

      headlines = ["Code INSEE", "Nom"].concat(headlines)
      cols = [mesh_elements.map((c)=> c.geo_code), mesh_elements.map((c)=> c.name)].concat(cols)
      format_table = [(f)=>f, (f)=>f].concat(format_table)
      format_csv = [(f)=>f, (f)=>f].concat(format_csv)
      align = ["l", "l"].concat(align)

      let rows = cols_to_rows(cols).sort((a, b)=> ('' + a[1]).localeCompare(b[1])) // tri par ordre alphabétique des noms

      return {headlines, rows, format_table, format_csv, align}
    } else if ("elements" in this.tables) {
      let {headlines, cols, format_table, format_csv, align} = this.tables.elements(objects, selected_filters)

      let rows = cols_to_rows(cols)

      return {headlines, rows, format_table, format_csv, align}
    } else {
        let headlines = [], rows = [], format_table = [], format_csv = [], align = [];
        return {headlines, rows, format_table, format_csv, align}
    }
  }

  updateDataSource(objects){
    if(this.data_source_from_request){
      this.data_source = this.data_source_function(objects)
    }
  }

  setDatasets(all_datasets){
    let concerned_datasets = this.datasets_names.map(n => all_datasets[n])

    /*let meshes = concerned_datasets.map(d => d.meshes).filter(m => m !== null && m.length > 0)
    meshes = meshes.length > 0 ? meshes : [["com", "epci", "dep"]]
    meshes = meshes.reduce((a, c) => a.filter(i => c.includes(i)))
    this.meshes = Object.fromEntries(meshes.map(m => [m, meshes_labels[m]]))
    this.mesh_init = meshes.length > 0 ? meshes[0] : null*/

    let allMeshesSet = concerned_datasets.map(d => d.meshes).map((mesh_types)=> createMeshesSetFromTypes(mesh_types))
    this.meshesSet = intersectMeshesSet(allMeshesSet)
    this.mesh_init = this.meshesSet.getMeshInit()

    let datasets = concerned_datasets.map(d => ({
      name_api: d.endpoint,
      is_mesh_element: d.is_mesh_element,
    }))
    this.datasets = datasets

    let yearsSet = new YearsSet(concerned_datasets.map(d => new Year({
      name_dataset: d.endpoint,
      name_year: d.name_year,
      years: d.years,
    })))
    this.yearsSet = yearsSet
  }
}
