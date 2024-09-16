import {Layer} from 'ol/layer.js';

import * as d3 from "d3";

import {toLonLat} from 'ol/proj.js';
import {context2d} from '../utilities.js'


export class GeojsonLayer extends Layer {
      constructor(geojson) {
        super(geojson);

        this.geojson = geojson

        this.init = true
        this.canvas =  d3.create("canvas").style('position', 'absolute').attr("class", "ol-layer").node();
      }

      getSourceState() {
        return 'ready';
      }

      render(frameState) {
        if (this.init){
          this.postrender(frameState)
          this.init = false
        }
        return this.canvas;
      }

      prerender(frameState) {
        const width = frameState.size[0];
        const height = frameState.size[1];

        let context = context2d(this.canvas, width, height)
        context.clearRect(0, 0, width, height);
      }

      postrender(frameState) {
        const width = frameState.size[0];
        const height = frameState.size[1];

        let context = context2d(this.canvas, width, height)

        let center = toLonLat(frameState.viewState.center)
        let scale = Math.pow(2, 8 + frameState.viewState.zoom ) / (2 * Math.PI)
        const angle = (-frameState.viewState.rotation * 180) / Math.PI;

        const d3Projection = d3.geoMercator()
          .scale(scale)
          .center(center)
          .translate([width / 2, height / 2])
          .angle(angle);

        let d3Path = d3.geoPath().projection(d3Projection).context(context);

        context.beginPath()
        context.lineWidth = 1
        context.strokeStyle = "white"
        context.fillStyle = "skyblue"
        context.fillOpacity = 0.5
        this.geojson.features.forEach((f, i) => {
          d3Path(f)
        });

        context.fill()
        context.stroke()
      }
    }
