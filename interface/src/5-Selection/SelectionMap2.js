import React from 'react';
import * as d3 from "d3";
import * as topojson from "topojson";

import LegendAAV from "./LegendAAV";
import Info from "../f-Utilities/Info";
import SourcesRow from "../f-Utilities/SourcesRow";
import SelectionMapInfo from "./SelectionMapInfo";

import {c_violet, c_gradient_greens, c_gradient_reds} from "../a-Graphic/Colors"

import {context2d_id, createFeaturesFromCommuneAttribute} from "./utilities.js"
import {buildCommunesLayer, buildNamesLayer, buildHoverLayer, buildSelectedCommunesLayer} from "./selection_map_functions.js"

import {typo_map_name} from "./typo_aav.js"


class SelectionMap extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      select_by: "epci",
      transform_init: d3.zoomIdentity,
      transform: d3.zoomIdentity,
      transform_ends: true,
      info: {
        geo_code: null
      }
    };
  }

selected_regions = ["11", "24", "27", "28", "32", "44", "52", "53", "75", "76", "84", "93", "94", "04", "02", "01", "03"] //, "06"]

  selectBy = (by) => {
       this.setState({
         select_by: by
       })
   }

   addSelection = (new_c_selected_geo_code) => {
       const communes_attr = this.props.data_selection_map.communes_attr
       new_c_selected_geo_code = new_c_selected_geo_code.filter(c=> this.selected_regions.includes(communes_attr.get(c).reg))

       let c_selected_geo_code = this.props.selected_communes
       if(new_c_selected_geo_code.every(c=>c_selected_geo_code.includes(c))){
         c_selected_geo_code = c_selected_geo_code.filter(c => !new_c_selected_geo_code.includes(c))
       } else {
         let c_to_add = new_c_selected_geo_code.filter((c)=>!c_selected_geo_code.includes(c))
         c_selected_geo_code = c_selected_geo_code.concat(c_to_add)
       }
       this.props.updateSelectedCommunes(c_selected_geo_code)
   }

   clearSelection = () => {
     this.props.updateSelectedCommunes([])
   }

    zoomMap = (direction) => {
      let current_trans = this.state.transform,
          factor = 2,
          target_k
      if(direction>0){
        target_k = current_trans.k*factor
      } else {
        target_k = current_trans.k/factor
      }
      target_k = Math.max(Math.min(target_k, 15), 1)
      if (target_k !== current_trans.k){
        let {width, height} = document.getElementById("map_layers").getBoundingClientRect()
        let center = {x: width/2, y:height/2}
        let target_x = (current_trans.x - center.x)*target_k/current_trans.k + center.x
        target_x = Math.min(Math.max(target_x, -width*(target_k-1)), 0)
        let target_y = (current_trans.y - center.y)*target_k/current_trans.k + center.y
        target_y = Math.min(Math.max(target_y, -height*(target_k-1)), 0)
        let new_transform = new d3.ZoomTransform(target_k, target_x, target_y)
        d3.select("#map_layers").transition().ease(d3.easePolyOut).duration(500).call(this.zoom.transform, new_transform)
      }
    }

   updateInfo = (code_commune) => {
     const {communes_attr, epci_attr,  arr_attr,  dep_attr, reg_attr, aav_attr} = this.props.data_selection_map
     if (code_commune === null){
       this.setState({info: {geo_code: null}})
     } else {
       let code_epci = communes_attr.get(code_commune).epci,
           code_arr = communes_attr.get(code_commune).arr,
           code_dep = communes_attr.get(code_commune).dep,
           code_aav =communes_attr.get(code_commune).aav,
           code_typo_aav = communes_attr.get(code_commune).typo_aav,
           name_commune = communes_attr.get(code_commune).name,
           name_epci = epci_attr.get(code_epci).epci_name,
           name_dep = dep_attr.get(code_dep).dep_name,
           name_arr = Array.from(arr_attr.keys()).includes(code_arr) ? arr_attr.get(code_arr).arr_name : "Sans arrondissement",
           name_aav = aav_attr.get(code_aav).aav_name,
           name_typo_aav = typo_map_name.get(code_typo_aav)
        this.setState({
          info: {
            geo_code: code_commune,
            name_commune: name_commune,
            name_epci: name_epci,
            name_arr: name_arr,
            name_dep: name_dep,
            name_aav: name_aav,
            name_typo_aav: name_typo_aav,
          }
        })
    }
   }

  componentDidMount() {
      const {topology_light, communes_with_emd_added, communes_with_emd_not_added,
        communes_attr, epci_attr,  arr_attr,  dep_attr, reg_attr, aav_attr} = this.props.data_selection_map

      const selected_regions = this.selected_regions

      const width = document.getElementById("map_layers").getBoundingClientRect().width;
      const height = width * 0.9 //window.innerHeight - 100;
      const margin = 1;

      const map_extent = [[margin, margin], [width - 2*margin, height - 2*margin]]

      d3.select("#map_layers").attr("style", "height : " + height + "px")
      d3.select("#map_layers_utilities").attr("style", "height : " + height + "px; position: absolute; top: 0; width : 0")
      d3.select("#sources_c").attr("style", "width : " + width*2/3 + "px; background-color: var(--background-t);")



      // PROJECTION
      console.log(communes_attr)
      let outline = topojson.merge(topology_light, topology_light.objects.com.geometries.filter((c)=>selected_regions.includes(communes_attr.get(c.properties.codgeo).reg))) // lighter to compute projection
      let projection = this.projection = d3.geoIdentity().reflectY(true) // here the file is already projected
          .fitExtent(map_extent, outline)     //make the map projection fit into size of screen minus margin on all sides



      // --COMMUNES
      let communes = this.communes = topojson.feature(topology_light, topology_light.objects.com)
      console.log("sort")
      let t = performance.now()
      let communes_sorted = this.communes_sorted = communes.features
          .filter((c)=> selected_regions.includes(communes_attr.get(c.properties.codgeo).reg))
          .sort((a,b) => communes_attr.get(a.properties.codgeo).typo_aav > communes_attr.get(b.properties.codgeo).typo_aav ? 1 : -1)
      console.log(t - performance.now())
      let com_feature_by_code = this.com_feature_by_code = new Map(communes.features.map((c, i)=> [c.properties.codgeo, c]))

      // --EMD COMMUNES
      let emd_added = this.emd_added = topojson.merge(topology_light, topology_light.objects.com.geometries.filter((c) => communes_with_emd_added.includes(c.properties.codgeo)))
      let emd_to_add = this.emd_to_add = topojson.merge(topology_light, topology_light.objects.com.geometries.filter((c) => communes_with_emd_not_added.includes(c.properties.codgeo)))

      // --REGIONS
      let regions = this.regions = createFeaturesFromCommuneAttribute(topology_light, communes_attr, "reg", selected_regions)
      let reg_feature_by_code = this.reg_feature_by_code = new Map(regions.features.map((e)=> [e.properties.code_reg, e]))

      // --DEPARTEMENTS
      let departements = this.departements = createFeaturesFromCommuneAttribute(topology_light, communes_attr, "dep", selected_regions)
      let dep_feature_by_code = this.dep_feature_by_code = new Map(departements.features.map((e)=> [e.properties.code_dep, e]))

      // --ARRONDISSEMENTS
      let arrondissements = this.arrondissements = createFeaturesFromCommuneAttribute(topology_light, communes_attr, "arr", selected_regions)
      let arr_feature_by_code = this.arr_feature_by_code = new Map(arrondissements.features.map((e)=> [e.properties.code_arr, e]))

      // --EPCI
      let epci = this.epci = createFeaturesFromCommuneAttribute(topology_light, communes_attr, "epci", selected_regions)
      let epci_feature_by_code = this.epci_feature_by_code = new Map(epci.features.map((e)=> [e.properties.code_epci, e]))

      // -- names
      let cheflieu_arr = this.cheflieu_arr = arrondissements.features.map(f=>f.properties.code_arr).filter(arr=>Array.from(arr_attr.keys()).includes(arr)).map(d=>communes_attr.get(arr_attr.get(d).arr_chef_lieu))
      let cheflieu_dep = this.cheflieu_dep = departements.features.map(f=>f.properties.code_dep).map(d=>communes_attr.get(dep_attr.get(d).dep_chef_lieu))
      let cheflieu_reg = this.cheflieu_reg = regions.features.map(f=>f.properties.code_reg).map(d=>communes_attr.get(reg_attr.get(d).reg_chef_lieu))

      let get_names = this.get_names = (k) => k > 2 ? (k > 6 ? cheflieu_arr : cheflieu_dep) : cheflieu_reg

      let ctxt_communes = this.ctxt_communes = context2d_id("map_communes", width, height)
      buildCommunesLayer(ctxt_communes, projection, this.state.transform,
        communes_attr, communes_sorted, epci, arrondissements, departements, this.state.select_by)

      let ctxt_names = this.ctxt_names = context2d_id("map_names", width, height)
      buildNamesLayer(ctxt_names, projection, this.state.transform,
        communes_attr, communes_sorted, epci, arrondissements, departements, emd_added, emd_to_add, get_names(1))


      let ctxt_hover = this.ctxt_hover = context2d_id("map_hovered", width, height)

      let path2154 = d3.geoPath(projection, ctxt_hover)
      // to identify communes when flying over map
      let centroids = this.centroids = communes.features.map(f => path2154.centroid(f))
      let delaunay  = this.delaunay = d3.Delaunay.from(centroids)

      buildHoverLayer(ctxt_hover, projection, this.state.transform,
        communes_attr, epci_attr, dep_attr, arr_attr, aav_attr,
        epci_feature_by_code, arr_feature_by_code, dep_feature_by_code,
        delaunay, centroids,
        communes,
        this.state.select_by, this.addSelection, this.updateInfo, this.selected_regions)


      let ctxt_selected = this.ctxt_selected = context2d_id("map_selected", width, height)
      buildSelectedCommunesLayer(ctxt_selected, projection, this.state.transform,
        com_feature_by_code, this.props.selected_communes)

      let zoom = this.zoom = d3.zoom()
          .scaleExtent([1, 15])
          .translateExtent(map_extent)
          .on("start", ({transform}) => this.setState({transform_init: transform, transform_ends: false}))
          .on("zoom", ({transform}) => this.setState({transform: transform, transform_ends: false}))
          .on("end", ({transform}) => this.setState({transform: transform, transform_ends: true}))
      d3.select("#map_layers").call(zoom);
  }

  componentDidUpdate(prevProps, prevState){
    const {topology_light, communes_attr, epci_attr,  arr_attr,  dep_attr, aav_attr} = this.props.data_selection_map

    if(prevState.info === this.state.info){

      if((this.state.transform_ends && this.state.transform_init !== this.state.transform) || prevState.select_by !== this.state.select_by){
        buildCommunesLayer(this.ctxt_communes, this.projection, this.state.transform,
          communes_attr, this.communes_sorted, this.epci, this.arrondissements, this.departements, this.state.select_by)

        buildHoverLayer(this.ctxt_hover, this.projection, this.state.transform,
          communes_attr, epci_attr, dep_attr, arr_attr, aav_attr,
          this.epci_feature_by_code, this.arr_feature_by_code, this.dep_feature_by_code,
          this.delaunay, this.centroids,
          this.communes,
          this.state.select_by, this.addSelection, this.updateInfo, this.selected_regions)
      }
      if (!this.state.transform_ends && this.state.transform_init !== this.state.transform){
        let {width, height} = this.ctxt_communes.canvas.getBoundingClientRect();
        this.ctxt_communes.clearRect(0,0,width, height)
        this.ctxt_hover.clearRect(0,0,width, height)
      }

      if(this.state.transform_ends){
          buildSelectedCommunesLayer(this.ctxt_selected, this.projection, this.state.transform,
            this.com_feature_by_code, this.props.selected_communes)
      }
      if (!this.state.transform_ends && this.state.transform_init !== this.state.transform){
        let {width, height} = this.ctxt_selected.canvas.getBoundingClientRect();
        this.ctxt_selected.clearRect(0,0,width, height)
      }

      buildNamesLayer(this.ctxt_names, this.projection, this.state.transform,
        communes_attr, this.communes_sorted, this.epci, this.arrondissements, this.departements, this.emd_added, this.emd_to_add, this.get_names(this.state.transform.k))
    }
  }

  render() {
    const typo_zaav = [{"libelle":"< 50 000 hab.","couleur_pole":"#F6B7C2","couleur_couronne":"#F5F0AF"},
                       {"libelle":"50 000 - 200 000 hab.","couleur_pole":"#F15D7D","couleur_couronne":"#EDE049"},
                       {"libelle":"200 000 - 700 000 hab.","couleur_pole":"#E40038","couleur_couronne":"#FFB520"},
                       {"libelle":"> 700 000 hab.","couleur_pole":"#A91535","couleur_couronne":"#EE9008"},
                       {"libelle":"Hors attraction des villes","couleur":"#F3F2F0"}]
    const select_by = {com: "Commune", epci: "EPCI", arr: "Arrondissement", dep: "Département"}


    const {topology_light, communes_attr, epci_attr,  arr_attr,  dep_attr, aav_attr} = this.props.data_selection_map

    return(
    <div>

      <div className="row">
        <div className="col-12">
          <div className="row mt-3">
            <div className="col-auto">
              <h2 className="nav selected">Sélection du territoire</h2>
            </div>
          </div>

          <div className="row mt-3 mb-5">
            <div className="col-6">
              <p>De nombreuses autorités organisatrices de la mobilité (AOM) sont des EPCIs, on les met donc en avant sur la carte ci-dessous.
              Cependant, <b>la mobilité s'étend souvent au-delà des contours administratifs</b>.
              C'est pourquoi on représente également les aires d'attraction des villes (AAV) sur la carte afin d'aider à ajuster le périmètre d'étude lorsque c'est pertinent.</p>
            </div>
          </div>

          <div className="row">
            <div className="col-12 col-lg-8">
              <div id="map_layers">
                <canvas id="map_communes" style={{position: "absolute"}}/>
                <canvas id="map_names" style={{position: "absolute"}}/>
                <canvas id="map_selected" style={{position: "absolute"}}/>
                <canvas id="map_hovered" style={{position: "absolute"}}/>
              </div>
              <div id="map_layers_utilities" style={{position: "absolute", top: 0}}>
                <p id="zoom_p" className="button_zoom p-1" onClick={this.zoomMap.bind(this, +1)} style={{position: "absolute", left: "10px", top: "10px"}}>+</p>
                <p id="zoom_m" className="button_zoom p-1" onClick={this.zoomMap.bind(this, -1)} style={{position: "absolute", left: "10px", top: "50px", lineHeight: 0.66}}>-</p>
              </div>
              <div id="sources_c">
                <SourcesRow selected_sources={Object.values(this.props.sources)}/>
              </div>
            </div>

            <div className="col-12 col-lg-4 mt-4 mt-lg-0 d-flex flex-column">
              <div className="row justify-content-between h-100">

                <div className="col-12 col-sm-6 col-lg-12 mb-5 mb-lg-0 align-self-start">

                  <div className="row">
                    <div className="col-auto p-2" id="legend_selection">
                      <LegendAAV />

                      <p className="mt-2"><b>Couverture des enquêtes mobilités locales (EMD, EDGT, EMC²)</b></p>
                      <p className="mb-1"><i>(affichée au zoom)</i></p>

                      <div className="row no-gutters align-items-center">
                        <div className="col-auto mr-3">
                          <div style={{width: "50px", borderBottom: "3px solid " + c_violet}}></div>
                        </div>
                        <div className="col-auto">
                          <p>Enquête disponible</p>
                        </div>
                      </div>

                      <div className="row no-gutters align-items-center">
                        <div className="col-auto mr-3">
                          <div style={{width: "50px", borderBottom: "3px dashed " + c_violet}}></div>
                        </div>
                        <div className="col-auto">
                          <p>Enquête existante mais à ajouter</p>
                        </div>
                      </div>

                    </div>
                  </div>

                </div>


                <div className="col-12 col-sm-6 col-lg-12  align-self-start align-self-lg-end">
                  <div className="row mb-4">
                    <SelectionMapInfo info={this.state.info}/>
                  </div>

                  <div className="row align-items-center mb-4">
                    <div className="col-12 col-sm-auto mb-2">
                      <p>Sélectionner par :</p>
                    </div>
                    <div className="col-auto">
                      <div className="btn-group select_by_btn" role ="group">
                        {Object.keys(select_by).map(k=>
                            <button type="button"
                               key={k}
                               onClick={this.selectBy.bind(this, k)}
                               className={this.state.select_by === k ? "btn active p-1 pl-2 pr-2" : "btn p-1 pl-2 pr-2"}>{select_by[k]}</button>
                        )}
                        </div>
                      </div>

                  </div>

                  <div className="row justify-content-between">
                    <div className="col-auto">
                      <p id="reset" className="button p-1 pl-2 pr-2" onClick={this.clearSelection.bind(this)}>Effacer la sélection</p>
                    </div>
                    <div className="col-auto">
                      <p id="validation" className="button p-1 pl-2 pr-2" onClick={this.props.loadTerritory.bind(this, "",
                                                                                                                      this.props.selected_communes,
                                                                                                                      this.props.selected_communes.map((c)=>1))}>Valider la sélection →</p>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          </div>

        </div>
      </div>


    </div>
    )
  }
}

export default SelectionMap;
