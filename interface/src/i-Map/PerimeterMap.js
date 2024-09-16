import React, { Component } from 'react';

import * as d3 from "d3";

import * as ol from "ol";
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import {fromLonLat, toLonLat} from 'ol/proj.js';
import {getCenter, getWidth} from 'ol/extent.js';
import VectorTileLayer from 'ol/layer/VectorTile.js';
import VectorTileSource from 'ol/source/VectorTile.js';
import MVT from 'ol/format/MVT.js';
import {applyBackground, applyStyle, stylefunction} from 'ol-mapbox-style';
import "ol/ol.css";
import {defaults} from 'ol/interaction/defaults';

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

99: NoChoroLayer
100: Mesh

200: ChoroLayer

300: Perimeter
301: Hover

500: Paths

600: Circle

1000: Names

1200: Legend
*/

class PerimeterMap {
  constructor(id, styles, geo) {
   this.id = id
   this.layers = []

   // legend layout
   let paddingMap = 5,
       paddingLegend = 0,
       marginLegend = 0,
       spacingLegendElements = 0,
       widthLegend = 0;

   const view = new View({
     enableRotation: false,
     maxZoom: 15,
     minZoom: 6
   });

   const map = this.map = new Map({
     layers: [],
     controls: [],
     interactions: defaults({mouseWheelZoom: false}),
     target: id,
     view: view,
   });

   /*
   // disable scroll wheel zoom
   map.getInteractions().forEach((interaction, i) => {
     if(interaction.constructor.name === "MouseWheelZoom"){
       interaction.setActive(false)
     }
   });*/

   // set popup
   map.set("popup", new MapPopup(map))

   // set domain
   view.fit(d3.geoBounds(geo.perimeter).map(c=>fromLonLat(c)).flat(), {padding: [paddingMap, widthLegend + 2 * marginLegend + paddingMap, paddingMap, paddingMap]})

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
   fg_layer.setZIndex(1000)
   map.addLayer(fg_layer)

   // mesh layer
   const mesh_layer = this.mesh_layer = new MeshLayer({
     mesh_lines: geo.mesh_lines,
     mesh_outline: geo.mesh_outline
   });
   mesh_layer.setZIndex(100)
   map.addLayer(mesh_layer);

    // no choropleth layer
    const no_choro_layer = this.no_choro_layer = new NoChoroLayer({
      mesh_outline: geo.mesh_outline
    });
    no_choro_layer.setZIndex(99)
    map.addLayer(no_choro_layer)

    // perimeter layer
    const perimeter_layer = new PerimeterLayer({
      perimeter: geo.perimeter
    });
    perimeter_layer.setZIndex(300)
    map.addLayer(perimeter_layer);

   // hover layer
   const hover_layer = this.hover_layer = new HoverLayer(geo.mesh);
   hover_layer.setZIndex(301)
   hover_layer.set("className", "allow_hover_layer")
   map.addLayer(hover_layer);

   // set interactions
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

   map.on('pointermove', onMove);
   d3.select("#"+id).on("mouseout", clearHover)
  }

  endMap(){
    this.map.on("moveend", null)
    this.map.on("movestart", null)
    this.map.on("pointermove", null)
    this.map.getLayers().forEach((layer, i) => {
      this.removeLayer(layer)
    });
  }

}

export default PerimeterMap;
