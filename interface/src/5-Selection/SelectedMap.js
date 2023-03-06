import React, { Component } from 'react';
import * as d3 from "d3";
import proj4 from "proj4";
import proj4d3 from "proj4d3";
import booleanPointInPolygon from "@turf/boolean-point-in-polygon";
import * as topojson from "topojson";

import LegendAAV from "./LegendAAV"
import Info from "../f-Utilities/Info"

import {c_light, c_green_text_t, c_violet, c_selection_zones} from "../a-Graphic/Colors"

import {context2d, delaunay_nextring, createStripePatternCanvas,
  hoverInfo} from "./utilities.js"


const L = window.L;

class SelectedMap extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      default_info: "Survoler la carte pour afficher les informations de la commune. Cliquer pour modifier les zones.",
      zones: {},
      select_by_zone: 1
    };
  }

  selectBy = (byZone) => {
       this.setState({
         select_by_zone: byZone
       })
   }

  initMap = () => {
      let t0 = performance.now()

      var data = this.props.data
      var d_communes = this.props.communes
      var d_epci = this.props.epci
      var d_aav = this.props.aav
      var with_emd = this.props.with_emd

      const width = document.getElementById("selected_map_layers").getBoundingClientRect().width;
      const height = width * 3/4 //window.innerHeight - 100;
      const margin = 5;

      const map_extent = [[margin, margin], [width - 2*margin, height - 2*margin]]

      d3.select("#selected_map_layers").attr("style", "height : " + height + "px")

      const communes = document.getElementById("selected_map_communes")
      const zones = document.getElementById("selected_map_zones")
      const hovered = document.getElementById("selected_map_hovered")

      const ctxt_communes = context2d(communes, width, height)
      const ctxt_zones = context2d(zones, width, height)
      const ctxt_hovered = context2d(hovered, width, height)

      const typo_zaav = [{"code":"11","libelle":"Pôle AAV < 50 000 hab","couleur":"#F6B7C2"},
                         {"code":"12","libelle":"Pôle AAV 50 000 ↔ 200 000 hab","couleur":"#F15D7D"},
                         {"code":"13","libelle":"Pôle AAV 200 000 ↔ 700 000 hab","couleur":"#E40038"},
                         {"code":"14","libelle":"Pôle AAV > 700 000 hab","couleur":"#A91535"},
                         {"code":"15","libelle":"Pôle AAV > 700 000 hab","couleur":"#A91535"},
                         {"code":"21","libelle":"Couronne AAV < 50 000 hab.","couleur":"#F5F0AF"},
                         {"code":"22","libelle":"Couronne AAV 50 000 ↔ 200 000 hab.","couleur":"#EDE049"},
                         {"code":"23","libelle":"Couronne AAV 200 000 ↔ 700 000 hab.","couleur":"#FFB520"},
                         {"code":"24","libelle":"Couronne AAV > 700 000 hab.","couleur":"#EE9008"},
                         {"code":"25","libelle":"Couronne AAV > 700 000 hab.","couleur":"#EE9008"},
                         {"code":"30","libelle":"","couleur":"#F3F2F0"}]
      const typo_map_color = new Map( typo_zaav.map(d => [d.code, d.couleur]))
      const typo_map_name = new Map( typo_zaav.map(d => [d.code, d.libelle]))

      let communes_geo = topojson.feature(data, data.objects.a_com2022).features

      this.setState({map_extent: map_extent,
                     ctxt_communes: ctxt_communes,
                     ctxt_zones: ctxt_zones,
                     ctxt_hovered: ctxt_hovered,
                     typo_zaav: typo_zaav,
                     typo_map_color: typo_map_color,
                     typo_map_name: typo_map_name,
                     all_communes_geo: communes_geo,
                     width: width,
                     height: height
                   })

      console.log("init")
      console.log(performance.now() - t0)
    }

    buildMap = () => {
      let t0 = performance.now()
      const d_communes = this.props.communes
      const d_epci = this.props.epci
      const d_aav = this.props.aav
      const data = this.props.data
      const typo_map_color = this.state.typo_map_color
      const typo_map_name = this.state.typo_map_name
      const width = this.state.width
      const height = this.state.height
      const sel_com_geo_code = this.props.selected_communes


      // --COMMUNES
      let selected_communes = this.state.all_communes_geo.filter((c)=>sel_com_geo_code.includes(c.properties.codgeo))
      let communes_sorted = selected_communes.sort((a,b) => d_communes["typo_aav"][a.properties.codgeo] > d_communes["typo_aav"][b.properties.codgeo] ? 1 : -1)

      const sel_com_cat_com_aav = new Map(selected_communes.map((c) => [c.properties.codgeo, d_communes["cat_commune_aav"][c.properties.codgeo]]))
      const sel_com_typo_aav = new Map(selected_communes.map((c) => [c.properties.codgeo, d_communes["typo_aav"][c.properties.codgeo]]))
      const selected_communes_index = new Map(selected_communes.map((c, i) => [c.properties.codgeo, i]))

      const is_territory_metro = Array.from(sel_com_typo_aav.values()).includes("14") |
                                 Array.from(sel_com_typo_aav.values()).includes("15")

      // --ZONES
      function createZones(geo_codes){
        let max_typo_aav = Math.max(...geo_codes.map((g)=> sel_com_typo_aav.get(g).slice(1, 2)))

        let zones = []
        for (let g of geo_codes){
          let typo = sel_com_typo_aav.get(g)
          let cat = sel_com_cat_com_aav.get(g)

          if (is_territory_metro){
            if (typo.slice(1, 2) == max_typo_aav){
              if (cat == 11) zones.push([g,1])
              else if (cat == 12| cat == 13) zones.push([g,2])
              else zones.push([g,3])
            }
            else{
              zones.push([g,3])
            }
          } else {

              if (typo.slice(1, 2) == max_typo_aav){
                if (cat == 11 | cat == 12| cat == 13) zones.push([g,1])
                else zones.push([g,3])
              }
              else{
                if (cat == 11 | cat == 12| cat == 13) zones.push([g,2])
                else zones.push([g,3])
              }
          }
        }
        return new Map(zones)
      }
      const sel_com_zones = createZones(sel_com_geo_code)
      Object.keys(this.state.zones).forEach((geo_code)=>{
        if (sel_com_zones.has(geo_code)) sel_com_zones.set(geo_code, this.state.zones[geo_code])
      })

      this.props.updateSelectedZones(Array.from(sel_com_zones.values()))

      let zones_geo = [3, 2, 1].map((i)=>topojson.merge(data, data.objects.a_com2022.geometries.filter((c) => sel_com_zones.get(c.properties.codgeo) == i)))

      // PROJECTION
            /* const proj_mercator = d3.geoMercator()
                  .fitExtent(map_extent, outline);

            const epsg2154 = "+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
            proj4.defs([ ['EPSG:2154', `+title=France Lambert93 ${epsg2154}`] ])
            const proj_epsg2154 = proj4d3(epsg2154)
                .fitExtent(map_extent, outline) */
      let context  = this.state.ctxt_communes
      let ctxt_hovered  = this.state.ctxt_hovered
      let projection = d3.geoIdentity().reflectY(true) // here the file is already projected
          .fitExtent(this.state.map_extent, {type: "FeatureCollection", features:selected_communes})     //make the map projection fit into size of screen minus margin on all sides
      let path2154 = d3.geoPath(projection, context)

      // to identify communes when flying over map
      let centroids = selected_communes.map(f => path2154.centroid(f))
      let delaunay  = d3.Delaunay.from(centroids)

      let t1 = performance.now()
      console.log(t1 - t0)


      let j
      let move = (e) => {
        let ptMouse2154, l, c1, c2, testIn, j0, iter = 0
        const [x, y] = this ? d3.pointer(e) : [200, 200]
        j = j0 = delaunay.find(x, y, j)

        ptMouse2154 = projection.invert([x, y])
        testIn = booleanPointInPolygon(ptMouse2154, selected_communes[j])

          if (!testIn) {
            let current_ring = [j], kernel = [], next_ring

            while ( l === undefined && iter++ < 4) {
              next_ring = delaunay_nextring(delaunay, current_ring, kernel)

              l = next_ring.find(k => booleanPointInPolygon(ptMouse2154, selected_communes[k]))

              kernel = kernel.concat(current_ring)
              current_ring = next_ring
            }

            if (l !== undefined) j = l
            else j = undefined
          }

          if (j !== undefined) {
            let commune = selected_communes[j]
            let code_commune = commune.properties.codgeo,
            name_commune = commune.properties.libgeo,
            code_aav = d_communes["code_aav"][code_commune],
            code_type_aav = d_communes["typo_aav"][code_commune],
            name_aav = d_aav[code_aav],
            name_typo_aav = typo_map_name.get(code_type_aav)

            document.getElementById("info_selected").innerHTML = hoverInfo(name_commune, code_commune, name_aav, name_typo_aav)

            ctxt_hovered.clearRect(0, 0, width, height);

            // commune
            ctxt_hovered.beginPath()
            ctxt_hovered.fillStyle = typo_map_color.get(code_type_aav)
            d3.geoPath(projection, ctxt_hovered)(commune)
            ctxt_hovered.fill()

            ctxt_hovered.beginPath()

            let select_by_zone = this.state.select_by_zone
            ctxt_hovered.lineWidth = layout_zones[select_by_zone].strokeWidth
            ctxt_hovered.strokeStyle = layout_zones[select_by_zone].color
            let pattern = ctxt_hovered.createPattern(layout_zones_pattern[select_by_zone], 'repeat')
            ctxt_hovered.fillStyle = pattern
            d3.geoPath(projection, ctxt_hovered)(commune)
            ctxt_hovered.fill()
            ctxt_hovered.stroke()

            if (e.type == "click") {
              this.setState((prevState, props)=>{
                prevState[code_commune] = prevState.select_by_zone
                return {
                  zones: prevState
                }})
            }
          }
          else {
            document.getElementById("info_selected").innerHTML = `<p>${this.state.default_info}</p>`
            ctxt_hovered.clearRect(0, 0, width, height);
          }
      }
      d3.select("#selected_map_layers").on("touchmove mousemove click", move)


      /*
      function reset_selection(){
      }
      d3.select("#reset").on("click", reset_selection)
      */

      context.clearRect(0, 0, width, height);

      // COMMUNES
      context.beginPath()
      context.lineWidth = 1
      context.strokeStyle = "white"
      let last_typo

      for (let i = 0; i < communes_sorted.length; i++) {
        let c = communes_sorted[i]
        let typo = d_communes["typo_aav"][c.properties.codgeo]

        if (typo != last_typo) {
          context.fill()
          context.stroke()
          context.beginPath()
          context.fillStyle = typo_map_color.get(typo)
        }
        path2154(c)
        last_typo = typo
      }
      context.fill()
      context.stroke()

      // COMMUNES ZONES
      let layout_zones = {
        1: {color: c_selection_zones[0], strokeWidth: 3},
        2: {color: c_selection_zones[1], strokeWidth: 2},
        3: {color: c_selection_zones[2], strokeWidth: 1},
      }
      let layout_zones_pattern = {
        1: createStripePatternCanvas(1, layout_zones[1].strokeWidth, layout_zones[1].color),
        2: createStripePatternCanvas(0, layout_zones[2].strokeWidth, layout_zones[2].color),
        3: createStripePatternCanvas(2, layout_zones[3].strokeWidth, layout_zones[3].color)
      }

      zones_geo.forEach((c, i) => {
        let zone_id = 3 - i
        context.beginPath()
        context.lineWidth = layout_zones[zone_id].strokeWidth
        context.strokeStyle = layout_zones[zone_id].color

        let pattern = context.createPattern(layout_zones_pattern[zone_id], 'repeat')
        context.fillStyle = pattern

        path2154(c)
        context.fill()
        context.stroke()

        let ctxt_leg = d3.select("#leg_zone_" + zone_id).node().getContext("2d")
        let width = d3.select("#leg_zone_" + zone_id).node().width
        let height = d3.select("#leg_zone_" + zone_id).node().height
        ctxt_leg.fillStyle = pattern
        ctxt_leg.lineWidth = layout_zones[zone_id].strokeWidth
        ctxt_leg.strokeStyle = layout_zones[zone_id].color
        ctxt_leg.rect(0, 0, width, height)
        ctxt_leg.fill()
        ctxt_leg.stroke()
      });


      // COMMUNES NAMES
      /*
      context.font = "600 12px Source sans pro"
      context.lineWidth = 1.5
      context.lineCap  = "round"
      context.lineJoin = "round"
      context.fillStyle = "black"
      context.strokeStyle = 'rgba(255, 255, 255, 0.8)'
      context.textAlign = "center"

      communes_sorted.forEach((d) => {
          let xy = projection([+d.properties.xcl2154, +d.properties.ycl2154])
          let txt = typo_zones[d_communes["typo_aav"][d.properties.codgeo]]//d.properties.libgeo.replace('Saint','St').toUpperCase()
          context.strokeText(txt, xy[0], xy[1])
          context.fillText(txt, xy[0], xy[1])
        })
        */


      console.log(~~(performance.now() - t1) + ' ms')
  }

  componentDidMount(){
    this.initMap()
  }

  componentDidUpdate(prevProps, prevState){
    if (this.props.selected_communes !== prevProps.selected_communes |
        this.state.zones !== prevState.zones) this.buildMap()
  }

  render() {

    return(
    <div>
      <div className="row mb-5">
        <div className="col-4">
          <h2 className="bottom-line-green">Attribution de zones</h2>
        </div>
        <div className="col-8">
          <p className="mb-2">Découper le territoire en zones permettra <span className="highlight-green">d'étudier la répartition des flux et les différences de parts modales au sein et entre zones</span>.
          <Info content="Les flux vers l'extérieur du territoire sélectionné seront également proposés par défaut."/></p>
          <p className="mb-1">Pour une métropole, on identifie par exemple la commune centre, la première couronne et la deuxième couronne.
          Pour un territoire en milieu peu dense, on peut choisir une ou deux villes génératrices de déplacements.</p>
          <p>Une présélection est proposée suivant le découpage en aire d'attraction des villes.
          Cliquer sur le type de zone souhaité puis sur les communes pour modifier.</p>
        </div>
      </div>

      <div className="row">
        <div className="col-12">
          <div className="row">

              <div className="col-8">
                <div id="selected_map_layers">
                  <canvas id="selected_map_communes" style={{position: "absolute"}}/>
                  <canvas id="selected_map_zones" style={{position: "absolute"}}/>
                  <canvas id="selected_map_hovered" style={{position: "absolute"}}/>
                </div>
              </div>

              <div className="col-4 d-flex flex-column">

                <div className="row h-100 mb-3">
                  <div  className="col d-flex flex-column pl-2 pr-2">

                    <div className="row h-100">
                      <div className="col">
                            <LegendAAV/>

                            {[1, 2, 3].map((zone_id)=>
                            <div className="row no-gutters align-items-center mt-2">
                              <div className="col-auto mr-3">
                                <canvas id={"leg_zone_" + zone_id} width="65px" height="30px"/>
                              </div>
                              <div className="col">
                                <p><b>Zone {zone_id}</b></p>
                              </div>
                            </div>)}
                      </div>
                    </div>

                    <div className="row">
                        <div className="col" id="info_selected"><p>{this.state.default_info}</p></div>
                    </div>

                </div>
              </div>


                <div className="row pr-3">
                  <div className="col p-2" style={{backgroundColor: c_green_text_t}}>
                    <div className="row mb-3">
                      <div className="col-12">
                        <p>Sélectionner par commune pour attribuer :</p>
                      </div>
                    </div>

                    <div className="row align-items-center">
                      {[1, 2, 3].map((zone_id)=>
                      <div className="col-auto">
                        <p onClick={this.selectBy.bind(this, zone_id)}
                           style={{cursor: "pointer"}}
                           className={this.state.select_by_zone == zone_id ? "line bold-text" : ""}>Zone {zone_id}</p>
                      </div>)}
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

export default SelectedMap;
