import React, { Component } from 'react';
import * as d3 from "d3";
import proj4 from "proj4";
import proj4d3 from "proj4d3";
import booleanPointInPolygon from "@turf/boolean-point-in-polygon";
import * as topojson from "topojson";

import LegendAAV from "./LegendAAV";
import Info from "../f-Utilities/Info";
import SourcesP from "../f-Utilities/SourcesP";

import {c_light, c_green_text as c_green, c_green_text_t, c_violet} from "../a-Graphic/Colors"

import {context2d, delaunay_nextring, createStripePatternCanvas, hoverInfo} from "./utilities.js"


const L = window.L;

class SelectionMap extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      default_info: "Survoler la carte pour afficher les informations de la commune. Cliquer pour ajouter au territoire d'étude.",
      selected_communes: [],
      select_by_epci: true
    };
  }

  selectBy = (byEPCI) => {
       this.setState({
         select_by_epci: byEPCI
       })
   }

  componentDidMount() {
      const width = document.getElementById("map_layers").getBoundingClientRect().width;
      const height = width * 0.93 //window.innerHeight - 100;
      const margin = 1;

      const map_extent = [[margin, margin], [width - 2*margin, height - 2*margin]]

      d3.select("#map_layers").attr("style", "height : " + height + "px")

      const communes = document.getElementById("map_communes")
      const hovered = document.getElementById("map_hovered")
      const selected = document.getElementById("map_selected")

      const tooltip = d3.select("#info")

      const ctxt_communes = context2d(communes, width, height)
      const ctxt_hovered = context2d(hovered, width, height)
      const ctxt_selected = context2d(selected, width, height)

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


      function buildMap(data, d_communes, d_epci, d_aav, with_emd){
        let t0 = performance.now()

        /* const proj_mercator = d3.geoMercator()
              .fitExtent(map_extent, outline);

        const epsg2154 = "+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
        proj4.defs([ ['EPSG:2154', `+title=France Lambert93 ${epsg2154}`] ])
        const proj_epsg2154 = proj4d3(epsg2154)
            .fitExtent(map_extent, outline) */

        // PROJECTION
        let outline = topojson.merge(data, data.objects.a_com2022.geometries) // lighter to compute projection
        let context  = ctxt_communes
        let projection = d3.geoIdentity().reflectY(true) // here the file is already projected
            .fitExtent(map_extent, outline)     //make the map projection fit into size of screen minus margin on all sides
        let path2154 = d3.geoPath(projection, context)


        // --COMMUNES
        let communes = topojson.feature(data, data.objects.a_com2022)
        let communes_sorted = communes.features
            .sort((a,b) => d_communes["typo_aav"][a.properties.codgeo] > d_communes["typo_aav"][b.properties.codgeo] ? 1 : -1)
        let cf_i_by_geocode = new Map(communes.features.map((c, i)=> [c.properties.codgeo, i]))

        // --EMD COMMUNES
        let emd = topojson.merge(data, data.objects.a_com2022.geometries.filter((c) => with_emd.includes(c.properties.codgeo)))

        // --SELECTED COMMUNES GEOCODES
        var c_selected_geo_code = []
        var updateSelectedCommunes = this.props.updateSelectedCommunes

        // --DEPARTEMENTS
        let departements = topojson.feature(data, data.objects.a_dep2022)

        // --EPCI
        let epci = topojson.feature(data, data.objects.a_epci)
        let ef_i_by_code = new Map(epci.features.map((e, i)=> [e.properties.code_epci, i]))

        // to identify communes when flying over map
        let centroids = communes.features.map(f => path2154.centroid(f))
        let delaunay  = d3.Delaunay.from(centroids)

        console.log(performance.now() - t0)

        let zoom = d3.zoom()
            .scaleExtent([1, 15])
            .on("end", ({transform}) => zoomed(transform))
            //.on("zoom", ({transform}) => zoomed(transform))
        d3.select("#map_layers").call(zoom);


        let previous_transform

        function zoomed(transform) {
          let t2 = performance.now()

          if (previous_transform == transform) return // prevent from unuseful transformation
          previous_transform = transform

          let j
          let move = (e) => {
            let ptMouse2154, l, c1, c2, testIn, j0, iter = 0
            const [x, y] = this ? transform.invert(d3.pointer(e)) : [200, 200] // to adapt from pan & zoom transformation
            j = j0 = delaunay.find(x, y, j)

            ptMouse2154 = projection.invert([x, y])
            testIn = booleanPointInPolygon(ptMouse2154, communes.features[j])

              if (!testIn) {
                let current_ring = [j], kernel = [], next_ring

                while ( l === undefined && iter++ < 4) {
                  next_ring = delaunay_nextring(delaunay, current_ring, kernel)

                  l = next_ring.find(k => booleanPointInPolygon(ptMouse2154, communes.features[k]))

                  kernel = kernel.concat(current_ring)
                  current_ring = next_ring
                }

                if (l !== undefined) j = l
                else j = undefined
              }

              if (j !== undefined) {
                let commune = communes.features[j]
                let code_commune = commune.properties.codgeo,
                name_commune = commune.properties.libgeo,
                code_epci = d_communes["code_epci"][code_commune],
                code_aav = d_communes["code_aav"][code_commune],
                code_type_aav = d_communes["typo_aav"][code_commune],
                name_epci = d_epci[code_epci],
                name_aav = d_aav[code_aav],
                name_typo_aav = typo_map_name.get(code_type_aav)
                let h_epci = epci.features[ef_i_by_code.get(code_epci)]
                document.getElementById("info").innerHTML = hoverInfo(name_commune, code_commune, name_aav, name_typo_aav, name_epci)

                ctxt_hovered.save();
                ctxt_hovered.clearRect(0, 0, width, height);
                ctxt_hovered.translate(transform.x, transform.y);
                ctxt_hovered.scale(transform.k, transform.k);

                // commune
                ctxt_hovered.beginPath()
                ctxt_hovered.strokeStyle = c_green
                ctxt_hovered.lineWidth = 1.5/transform.k
                d3.geoPath(projection, ctxt_hovered)(commune)
                ctxt_hovered.stroke()

                // epci
                ctxt_hovered.beginPath()
                ctxt_hovered.strokeStyle = c_green
                ctxt_hovered.lineWidth = 2.5/transform.k
                //const stripePattern = ctxt_hovered.createPattern(createStripePatternCanvas(transform.k), "repeat")
                //ctxt_hovered.fillStyle = stripePattern
                d3.geoPath(projection, ctxt_hovered)(h_epci)
                //ctxt_hovered.fill()
                ctxt_hovered.stroke()

                ctxt_hovered.restore()

                if (e.type == "click") {
                  let new_c_selected_geo_code
                  if (this.state.select_by_epci) new_c_selected_geo_code = h_epci.properties.communes_geocodes
                  else new_c_selected_geo_code = [code_commune]

                  let c_to_add = new_c_selected_geo_code.filter((c)=>!c_selected_geo_code.includes(c))
                  c_selected_geo_code = c_selected_geo_code.concat(c_to_add)
                  updateSelectedCommunes(c_selected_geo_code)

                  // COMMUNES_SELECTED
                  ctxt_selected.save();
                  ctxt_selected.translate(transform.x, transform.y);
                  ctxt_selected.scale(transform.k, transform.k);

                  ctxt_selected.beginPath()
                  ctxt_selected.lineWidth = 1/transform.k
                  ctxt_selected.strokeStyle = c_green
                  ctxt_selected.fillStyle = c_green + "cc"

                  let path_selected = d3.geoPath(projection, ctxt_selected)
                  c_to_add.forEach((geocode) =>
                    path_selected(communes.features[cf_i_by_geocode.get(geocode)])
                  );
                  ctxt_selected.fill()
                  ctxt_selected.stroke()
                  ctxt_selected.restore()
                }

              }
              else {
                document.getElementById("info").innerHTML = `<p>${this.state.default_info}</p>`
                ctxt_hovered.clearRect(0, 0, width, height);
              }
          }
          d3.select("#map_layers").on("touchmove mousemove click", move)

          function reset_selection(){
            c_selected_geo_code = []
            updateSelectedCommunes(c_selected_geo_code)
            ctxt_selected.clearRect(0, 0, width, height);
          }
          d3.select("#reset").on("click", reset_selection)


          context.save();
          context.clearRect(0, 0, width, height);
          context.translate(transform.x, transform.y);
          context.scale(transform.k, transform.k);

          // COMMUNES
          context.beginPath()
          context.lineWidth = 0.5/transform.k
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

          // COMMUNES_SELECTED
          ctxt_selected.save();
          ctxt_selected.clearRect(0, 0, width, height);
          ctxt_selected.translate(transform.x, transform.y);
          ctxt_selected.scale(transform.k, transform.k);

          ctxt_selected.beginPath()
          ctxt_selected.lineWidth = 1/transform.k
          ctxt_selected.strokeStyle = c_green
          ctxt_selected.fillStyle = c_green + "cc"

          let path_selected = d3.geoPath(projection, ctxt_selected)
          c_selected_geo_code.forEach( geo_code => {
            path_selected(communes.features[cf_i_by_geocode.get(geo_code)])
            }
          )
          ctxt_selected.fill()
          ctxt_selected.stroke()
          ctxt_selected.restore()

          // EPCI
          context.beginPath()
          context.lineWidth = 0.75/transform.k
          context.strokeStyle = "#666"
          epci.features.forEach( d => {
            path2154(d)
            }
          )
          context.stroke()

          // DEPARTEMENTS
          context.beginPath()
          context.lineWidth = 1/transform.k
          context.strokeStyle = "#333"
          departements.features.forEach( d => {
            path2154(d)
            }
          )
          context.stroke()

          // COMMUNES EMD

          context.beginPath()
          context.lineWidth = 2.5/transform.k
          context.strokeStyle = c_violet
          path2154(emd)
          context.stroke()

          console.log(~~(performance.now() - t2) + ' ms')
          context.restore();
        }
        zoomed = zoomed.bind(this)

        zoomed(d3.zoomIdentity);
      }
      buildMap = buildMap.bind(this)

      buildMap(this.props.data, this.props.communes, this.props.epci,
               this.props.aav, this.props.with_emd)
  }

  render() {
    const typo_zaav = [{"libelle":"< 50 000 hab.","couleur_pole":"#F6B7C2","couleur_couronne":"#F5F0AF"},
                       {"libelle":"50 000 - 200 000 hab.","couleur_pole":"#F15D7D","couleur_couronne":"#EDE049"},
                       {"libelle":"200 000 - 700 000 hab.","couleur_pole":"#E40038","couleur_couronne":"#FFB520"},
                       {"libelle":"> 700 000 hab.","couleur_pole":"#A91535","couleur_couronne":"#EE9008"},
                       {"libelle":"Hors attraction des villes","couleur":"#F3F2F0"}]

    return(
    <div>
      <div className="row mt-5 mb-5">
        <div className="col-4">
          <h2 className="bottom-line-green">Sélection du périmètre</h2>
        </div>
        <div className="col-8">
          <p className="mb-2">Le diagnostic mobilité concerne la <span className="highlight-green">mobilité du quotidien des personnes</span>.
          Il propose une analyse des pratiques de déplacements de la population interne au territoire sélectionné.
          <Info content="Cela n'incluera pas les déplacements effectués au sein du territoire par des personnes qui n'y habitent pas."/></p>
          <p>De nombreuses autorités organisatrices de la mobilité (AOM) sont des EPCIs, c'est pourquoi on les met en avant sur la carte ci-dessous.
          Pourtant, <span className="highlight-green">si la mobilité est souvent traitée à l'échelle d'un EPCI,
          son organisation est liée à celle des bassins de vie</span>. Ces derniers sont
          formalisés par l'INSEE avec les aires d'attraction des villes (AAV).
          On les représente également sur la carte afin d'aider à ajuster le périmètre d'étude lorsque c'est pertinent.</p>

        </div>
      </div>

      <div className="row">
        <div className="col-12">
          <div className="row">

            <div className="col-8">
              <div id="map_layers">
              <canvas id="map_communes" style={{position: "absolute"}}/>
              <canvas id="map_selected" style={{position: "absolute"}}/>
              <canvas id="map_hovered" style={{position: "absolute"}}/>
              </div>
            </div>

            <div className="col-4 d-flex flex-column">
              <div className="row h-100 mb-3">
                <div  className="col d-flex flex-column pl-2 pr-2">
                  <div className="row h-100">

                    <div className="col">
                        <LegendAAV />

                        {/*<div className="row no-gutters align-items-center mb-3">
                          <div className="col-auto mr-3">
                            <div style={{height: "1px", width: "50px", backgroundColor: "#666"}}></div>
                          </div>
                          <div className="col">
                            <p><b>EPCIs</b></p>
                          </div>
                        </div>*/}

                        <div className="row no-gutters align-items-center">
                          <div className="col-auto mr-3">
                            <div style={{height: "4px", width: "50px", backgroundColor: c_violet}}></div>
                          </div>
                          <div className="col">
                            <p><b>Territoires avec une enquête déplacement (EMD, EDGT, EMC²) disponible</b></p>
                          </div>
                        </div>

                    </div>

                  </div>

                  <div className="row">
                    <div className="col" id="info"><p>{this.state.default_info}</p></div>
                  </div>

                </div>
              </div>
              <div className="row pr-3">
                <div className="col p-2" style={{backgroundColor: c_green_text_t}}>
                  <div className="row align-items-center mb-3">
                    <div className="col-auto">
                      <p>Sélectionner par :</p>
                    </div>
                    <div className="col-auto">
                      <p onClick={this.selectBy.bind(this, true)}
                         style={{cursor: "pointer"}}
                         className={this.state.select_by_epci ? "line bold-text" : ""}>EPCI</p>
                    </div>
                    <div className="col-auto">
                      <p onClick={this.selectBy.bind(this, false)}
                         style={{cursor: "pointer"}}
                         className={this.state.select_by_epci ? "" : "line bold-text"}>Commune</p>
                    </div>
                  </div>
                  <div className="row">
                    <div className="col-auto">
                      <p id="reset" className="button p-1 pl-2 pr-2">Effacer la sélection</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-5">
          <SourcesP sources={this.props.sources} concerned={["map", "epci", "aav"]} />
        </div>
      </div>

    </div>
    )
  }
}

export default SelectionMap;
