import {Layer} from 'ol/layer.js';

import * as d3 from "d3";

import {toLonLat} from 'ol/proj.js';
import {context2d} from '../utilities.js'

import {c_missing_data} from '../../a-Graphic/Colors'
import {strokeWidth} from '../../a-Graphic/Layout'

import {ChoroLegend} from '../Legends/ChoroLegend'
import {layers_z_index} from '../map_z_index'


export class ChoroLayer extends Layer {
      constructor(options) {
        super(options);
        let {geojson, getValue, getLabel, legend} = options;
        let scale = d3.scaleThreshold()
                    .domain(legend.thresholds.slice(1, -1))
                    .range(legend.colors);

        // set mesh labels to display on hover
        this.mesh_labels = new Map(geojson.features.map((f) => [f.properties.codgeo, getLabel(f.properties)]))

        // sort elements with data | no data
        let wd_elements = geojson.features.filter((f) => getValue(f.properties) !== undefined && getValue(f.properties) !== null)
        wd_elements = this.wd_elements = d3.groups(wd_elements, (d) => scale(getValue(d.properties)))

        let nd_elements = this.nd_elements = geojson.features.filter((f) => getValue(f.properties) === undefined || getValue(f.properties) === null)

        // set legend
        this.legend = new ChoroLegend({
          ...legend,
          no_data: nd_elements.length > 0
        })

        this.init = true
        this.z_index = layers_z_index.choroLayer
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

        // elements with data grouped
        this.wd_elements.forEach((group, i) => {
          let [color, items] = group

          context.beginPath()
          context.lineWidth = strokeWidth
          context.lineJoin = "round"
          context.strokeStyle = "white"
          context.globalAlpha = 0.85
          context.fillStyle = color

          items.forEach((f) => {
            d3Path(f)
          });

          context.fill()
          context.stroke()
        });

        // elements with no data
        context.beginPath()
        context.lineWidth = strokeWidth
        context.lineJoin = "round"
        context.strokeStyle = "white"
        context.globalAlpha = 0.85
        context.fillStyle = c_missing_data

        this.nd_elements.forEach((f) => {
          d3Path(f)
        });

        context.fill()
        context.stroke()
      }
    }
