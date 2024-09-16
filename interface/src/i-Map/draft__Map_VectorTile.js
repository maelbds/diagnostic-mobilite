import React, { Component } from 'react';


import Protobuf from "pbf"

import * as tilePainter from "tile-painter"
import * as tileStencil from "tile-stencil"
import * as vectorTileEsm from "vector-tile-esm"

import {context2d} from '../5-Selection/utilities'

const d3 = window.d3;
var VectorTile = require('@mapbox/vector-tile').VectorTile


class Map extends React.Component {
  constructor(props) {
   super(props);
  }

  componentDidMount(){

    async function loadStyle(){
      d3.json("attenue.json").then((res)=> {
        tileStencil.parseStyle(res).then((style)=> {
          draw_map(style)
        })
      })
    }

    function draw_map(styleDoc){
      console.log(styleDoc)

    const endpoint = (x, y, z) => "https://wxs-pgie.ign.fr/essentiels/geoportail/tms/1.0.0/PLAN.IGN/{z}/{x}/{y}.pbf"

    const width = 1200
    const height = 600

    const tileSize = 512


    const margin_tile = 20



    function mvtToGeoJson(mvt_layers) {
      let layers = {};
      Object.values(mvt_layers).forEach(layer => {
        layers[layer.name] = layer.toGeoJSON(tileSize);
      });
      return layers;
    }

    let parsedStyle = styleDoc


    const offscreenBackground = document.getElementById("offscreenBackground")
    const background = document.getElementById("backgroundMap")
    const wip = document.getElementById("wip")

    d3.select("#map_container").attr("style", "height : " + height + "px")

    const context = context2d(background, width, height);

    // CANVAS tiles
    let projection = d3.geoMercator()
      .center([-0.3036623, 46.3678027])
      .scale((Math.pow(2, 20) + 0) / (2 * Math.PI))
      .translate([width / 2, height / 2])
    let path = d3.geoPath(projection)

    let tile = d3.tile()
      .size([width, height])
      .scale(projection.scale() * 2 * Math.PI)
      .translate(projection([0, 0]))
      .tileSize(tileSize)


    let nameStyle = parsedStyle.layers.find(layer => ["toponyme_localite_ponc"].includes(layer["source-layer"]))
    console.log(nameStyle)
    console.log(parsedStyle)

    let painterFuncs = tilePainter
      .addPainters(parsedStyle, tile().scale)
      .layers.map(layer => layer.painter) //.filter(layer => !["toponyme_localite_ponc"].includes(layer["source-layer"])).map(layer => layer.painter)



    console.log("ok")
    console.log(tilePainter
      .addPainters(parsedStyle, tile().scale)
      .layers)
    console.log(painterFuncs)

    console.log(tile().scale)
    console.log(tileSize)

    let tiles = Promise.all(tile().map(async d => {
      //d.layers = new vectorTileEsm.VectorTile(new Protobuf(await d3.buffer(`https://wxs.ign.fr/essentiels/geoportail/tms/1.0.0/PLAN.IGN/13/4070/2907.pbf`))).layers; // Sign up for an API key: https://www.nextzen.org
      d.layers = new vectorTileEsm.VectorTile(new Protobuf(await d3.buffer(`https://wxs-pgie.ign.fr/essentiels/geoportail/tms/1.0.0/PLAN.IGN/${d[2]}/${d[0]}/${d[1]}.pbf`))).layers; // Sign up for an API key: https://www.nextzen.org
      return d;
    })).then((responses)=>{
        const [x0, y0] = responses[0];
        const [x1, y1] = responses[responses.length - 1];

        //const offscreenContext = context2d(offscreenBackground, (x1 - x0 + 1) * tileSize, (y1 - y0 + 1) * tileSize);
        const offscreenContext = context2d(offscreenBackground, width, height);
        const wipContext = context2d(wip, tile().scale + margin_tile, tile().scale + margin_tile);
        const labelBoxes = [];

        console.log("jjj")
      for (const t of responses){
        let [x, y, z]= t
        let layers = t.layers

        // Wrap the GeoJSON in an object to match the structure of style.sources
        const sources = {plan_ign: mvtToGeoJson(layers)};
        console.log(sources)
        // Paint all the layers to the Canvas, in order
        wipContext.clearRect(0, 0, tile().scale + margin_tile, tile().scale + margin_tile);
        painterFuncs.forEach(painter => {
          let a = painter(wipContext, z, sources, [])
          }
        );
        //wipContext.font = "12px source sans pro"
        let names = sources.plan_ign.toponyme_localite_ponc.features.forEach((f, i) => {
          //wipContext.fillText(f.properties.texte, f.geometry.coordinates[0], f.geometry.coordinates[1])
        });



        offscreenContext.drawImage(
          wipContext.canvas,
          (x + tile().translate[0]) * tile().scale + (x + tile().translate[0]) * margin_tile,
          (y + tile().translate[1]) * tile().scale + (y + tile().translate[1]) * margin_tile,
          tile().scale + margin_tile,
          tile().scale + margin_tile
        );

      }

      /*context.drawImage(
        offscreenContext.canvas,
        Math.round((x0 + tile().translate[0]) * tile().scale),
        Math.round((y0 + tile().translate[1]) * tile().scale),
        (x1 - x0 + 1) * tile().scale,
        (y1 - y0 + 1) * tile().scale
      );*/
    })



    /*
    for (const [x, y, image] of await Promise.all(tiles.map(([x, y, z]) => new Promise((resolve, reject) => {
      const image = new Image;
      image.onerror = reject;
      image.onload = () => resolve(image);
      image.src = url(x, y, z);
    }).then(image => [x, y, image])))) {




      offscreenContext.drawImage(image, (x - x0) * tileSize, (y - y0) * tileSize, tileSize, tileSize);
    }

    */

    //document.getElementById("map_container").innerHTML = context.canvas;






/*
    const svg = d3.create("svg")
      .attr("viewBox", [0, 0, width, height]);

  const tile = d3.tile()
      .extent([[0, 0], [width, height]])
      .tileSize(64)
      .clampX(false);

  const zoom = d3.zoom()
      .scaleExtent([1 << 8, 1 << 22])
      .extent([[0, 0], [width, height]])
      .on("zoom", ({transform}) => zoomed(transform));

  let image = svg.append("g")
      .attr("pointer-events", "none")
    .selectAll("image");

  svg
      .call(zoom)
      .call(zoom.transform, d3.zoomIdentity
        .translate(width >> 1, height >> 1)
        .scale(1 << 12));

  function zoomed(transform) {
    const tiles = tile(transform);
    const url = (x, y, z) => `https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&STYLE=normal&FORMAT=image/png&TILEMATRIXSET=PM&TILEMATRIX=${z}&TILEROW=${y}&TILECOL=${x}`

    image = image.data(tiles, d => d).join("image")
        .attr("xlink:href", d => url(...d3.tileWrap(d)))
        .attr("x", ([x]) => (x + tiles.translate[0]) * tiles.scale)
        .attr("y", ([, y]) => (y + tiles.translate[1]) * tiles.scale)
        .attr("width", tiles.scale)
        .attr("height", tiles.scale);

  }

  document.getElementById("map_container").appendChild(svg.node())*/
    }
    loadStyle();
  }

  render() {
    return(
      <div className="row">
        <div className="col">

        <div id="map_container">
          <canvas id="offscreenBackground" style={{position: "absolute"}}/>
          <canvas id="backgroundMap" style={{position: "absolute"}}/>
        </div>


        <div className="mt-5">
          <canvas id="wip" style={{position: "absolute", opacity: 1}}/>
        </div>

        </div>
      </div>
    )
  }
}

export default Map;
