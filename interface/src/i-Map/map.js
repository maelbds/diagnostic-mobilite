import React, { Component } from 'react';

import * as d3 from "d3";

import * as ol from "ol";
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import ScaleLine from 'ol/control/ScaleLine.js';
import Zoom from 'ol/control/Zoom.js';

import {defaults} from 'ol/interaction/defaults';

import {fromLonLat, toLonLat} from 'ol/proj.js';
import {getCenter, getWidth} from 'ol/extent.js';
import VectorTileLayer from 'ol/layer/VectorTile.js';
import VectorTileSource from 'ol/source/VectorTile.js';
import MVT from 'ol/format/MVT.js';
import {applyBackground, applyStyle, stylefunction} from 'ol-mapbox-style';
import "ol/ol.css";


import {HoverLayer} from './Layers/HoverLayer'
import {MeshLayer} from './Layers/MeshLayer'
import {NoChoroLayer} from './Layers/NoChoroLayer'
import {PerimeterLayer} from './Layers/PerimeterLayer'
import {LegendLayer} from './Layers/LegendLayer'
import {NamesLayer} from './Layers/NamesLayer'

import {MapPopup} from './MapPopup'


/*
Layers Z indexes :

0 : Background

9: NoChoroLayer
10: Mesh

20: ChoroLayer

30: Perimeter
31: Hover

50: Paths

60: Circle

100: Names

120: Legend
*/


class CustomMap {
  constructor(id, styles, geo) {
   this.id = id
   this.layers = []

   // legend layout
   let paddingMap = 15,
       paddingLegend = 5,
       marginLegend = 10,
       spacingLegendElements = 10,
       widthLegend = 200;

   const view = new View({
     enableRotation: false,
     maxZoom: 15,
     minZoom: 6
   });

   const zoom = new Zoom({zoomInTipLabel: "Zoom Avant", zoomOutTipLabel: "Zoom Arrière"})
   const scaleLine = new ScaleLine()

   const map = this.map = new Map({
     layers: [],
     controls: [zoom, scaleLine],
     interactions: defaults({mouseWheelZoom: false}),
     target: id,
     view: view,
   });

   // disable scroll wheel zoom
   /*map.getInteractions().forEach((interaction, i) => {
     if(interaction.constructor.name === "MouseWheelZoom"){
       interaction.setActive(false)
     }
   });*/

   // set popup
   map.set("popup", new MapPopup(map))

   // set domain
   view.fit(d3.geoBounds(geo.perimeter).map(c=>fromLonLat(c)).flat(), {padding: [paddingMap, widthLegend + 2 * marginLegend + paddingMap, paddingMap, paddingMap]})

   // background layer
   const bg_layer = new VectorTileLayer({
     declutter: true,
     source: new VectorTileSource({
       format: new MVT(),
       url: 'https://data.geopf.fr/tms/1.0.0/PLAN.IGN/{z}/{x}/{y}.pbf',
     }),
   });
   stylefunction(bg_layer, styles.style_epure, 'plan_ign');
   bg_layer.setZIndex(0)
   map.addLayer(bg_layer)

   // names layer
   const fg_layer = this.fg_layer = new VectorTileLayer({
     declutter: true,
     source: new VectorTileSource({
       format: new MVT(),
       url: 'https://data.geopf.fr/tms/1.0.0/PLAN.IGN/{z}/{x}/{y}.pbf',
     }),
     className: "ol-layer allow_hover_layer"
   });
   stylefunction(fg_layer, styles.style_names, 'plan_ign');
   fg_layer.setZIndex(100)
   map.addLayer(fg_layer)

   // manual names layer
   const names_layer = this.names_layer = new NamesLayer({
     mesh: geo.mesh
   });
   names_layer.setZIndex(101)
   names_layer.setVisible(false)
   this.map.addLayer(names_layer);

   // mesh layer
   const mesh_layer = this.mesh_layer = new MeshLayer({
     mesh_lines: geo.mesh_lines,
     mesh_outline: geo.mesh_outline
   });
   mesh_layer.setZIndex(10)
   map.addLayer(mesh_layer);

    // no choropleth layer
    const no_choro_layer = this.no_choro_layer = new NoChoroLayer({
      mesh_outline: geo.mesh_outline
    });
    no_choro_layer.setZIndex(9)
    map.addLayer(no_choro_layer)

    // perimeter layer
    const perimeter_layer = new PerimeterLayer({
      perimeter: geo.perimeter
    });
    perimeter_layer.setZIndex(30)
    map.addLayer(perimeter_layer);

   // hover layer
   const hover_layer = this.hover_layer = new HoverLayer(geo.mesh);
   hover_layer.setZIndex(31)
   hover_layer.set("className", "allow_hover_layer")
   map.addLayer(hover_layer);

   // legend layer
   const legend_layer = this.legend_layer = new LegendLayer({
     widthLegend: widthLegend,
     marginLegend: marginLegend,
     paddingLegend: paddingLegend,
     spacingLegendElements: spacingLegendElements,
   });
   legend_layer.setZIndex(120)
   map.addLayer(legend_layer);


   // set interactions
   function onMoveStart(e){
     e.map.getLayers().forEach((layer, i) => {
       if (typeof layer.prerender ==="function"){
       layer.prerender(e.frameState)}
     });
   }

   function onMoveEnd(e){
     let popup = e.map.get("popup")
     e.map.getLayers().forEach((layer, i) => {
       if (typeof layer.postrender ==="function"){
       layer.postrender(e.frameState, popup)}
     });
   }

   function onMove(e){
     let popup = e.map.get("popup")
     e.map.getLayers().forEach((layer, i) => {
       if (typeof layer.onHover ==="function"){
       layer.onHover(e.originalEvent, {
         frameState: e.frameState,
         popup: popup,
       })}
     });
   }

   function clearHover(){
     map.get("popup").hide()
     hover_layer.hide()
   }

   map.on("moveend", onMoveEnd)
   map.on("movestart", onMoveStart)
   map.on('pointermove', onMove);
   d3.select("#"+id).on("mouseout", clearHover)
  }

  // update mesh geometry
  updateMesh(options){
    let {geo, mesh} = options
    this.hover_layer.updateMesh(geo.mesh)
    this.mesh_layer.updateMesh({
      mesh_lines: geo.mesh_lines,
      mesh_outline: geo.mesh_outline
    })
    this.no_choro_layer.updateMesh({
      mesh_outline: geo.mesh_outline
    })

    // manage names
    if(mesh === "com"){
      this.fg_layer.setZIndex(100)
      this.names_layer.setVisible(false)
    } else {
      this.fg_layer.setZIndex(1)
      this.names_layer.updateMesh({mesh: geo.mesh})
      this.names_layer.setVisible(true)
    }
  }

  // update map layers
  updateLayers(new_layers){
    // reset layers
    this.layers.forEach((layer, i) => {
      layer.setSource(null)
      this.map.removeLayer(layer)
    });

    this.layers = new_layers

    // add new_layers
    new_layers.forEach((layer, i) => {
      layer.setZIndex(layer.z_index + i)
      this.map.addLayer(layer)
      if (typeof layer.addHover ==="function"){
        layer.addHover(this.map.get("popup"))
      }
    });

    // set elements variables
    let legend_layer = this.legend_layer

    // wait for map to render all elements
    this.map.on("postrender", (e) => {
      // add hover for svg elements
      new_layers.forEach((layer, i) => {
        if (typeof layer.addHover ==="function"){
          layer.addHover(this.map.get("popup"))
        }
      });

      // set legend
      let legend_elements = new_layers.filter((l) => "legend" in l).map((l) => l.legend)
      legend_layer.update(legend_elements)
    })

    // set hover label for mesh elements
    let mesh_labels = new_layers.filter((l) => "mesh_labels" in l).map((l) => l.mesh_labels)
    this.hover_layer.mesh_labels = mesh_labels


    // auto add mesh background when no choro layer
    /*if (!(this.no_choro_layer in this.map.getLayers())){
      console.log("no choro layer")
      console.log(this.map.getLayers())
      this.map.addLayer(this.no_choro_layer)
      this.layers.push(this.no_choro_layer)
    }*/

  }

  endMap(){
    this.map.on("moveend", null)
    this.map.on("movestart", null)
    this.map.on("pointermove", null)
    this.map.getAllLayers().forEach((layer) => {
      layer.setSource(null)
      this.map.removeLayer(layer)
    });
    this.map = null
  }

}

export default CustomMap;
