import {Layer} from 'ol/layer.js';

import {FlowLegend} from '../Legends/FlowLegend';

import * as d3 from "d3";
import {ascending, descending} from "d3";

import {toLonLat} from 'ol/proj.js';

import {c_yellow, c_light, c_gradient_reds} from '../../a-Graphic/Colors'
import {layers_z_index} from '../map_z_index'

const Plot = window.Plot
const radians = Math.PI / 180;


export class FlowLayer extends Layer {
    constructor(options) {
      super(options);

      this.geojson = options.geojson

      this.getValue = options.getValue
      this.getLabel = options.getLabel

      this.sortFeatures = options.sort
      this.filterFeatures = options.filter
      this.limitFeatures = options.limit

      this.bidirectionnal = options.bidirectionnal === undefined ? false : options.bidirectionnal

      this.allLabels = this.geojson.features.filter(this.filterFeatures).sort(this.sortFeatures).slice(0, this.limitFeatures).map(f => this.getLabel(f))

      this.thresholds = options.legend.thresholds.slice(1, -1)

      this.scaleColor = d3.scaleThreshold()
                  .domain(this.thresholds)
                  .range(options.legend.colors);
      this.scaleStroke = d3.scaleThreshold()
                  .domain(this.thresholds)
                  .range(options.legend.strokes);
      this.scaleCircle = d3.scaleThreshold()
                  .domain(this.thresholds)
                  .range(options.legend.radius);


      options.arrow = {
        insetStart: 5,
        insetEnd: 5,
        headAngle: 60,
        headLength: 5,
        bend: 7,
        sweep: 1
      }

      this.arrowOptions = options.arrow

      // set legend
      this.legend = new FlowLegend(options.legend)

      this.svg = d3.create("svg")
      .style('position', 'absolute')
      .attr("class", "ol-layer")
      .style("pointer-events", "none");
      this.init = false;
      this.z_index = layers_z_index.flowLayer
    }

    getSourceState() {
      return 'ready';
    }

    render(frameState) {
      if (!this.init) {
        this.postrender(frameState);
        this.init = true;
      }
      return this.svg.node();
    }

    prerender(frameState) {
      this.svg.selectAll("*").remove();
    }

    postrender(frameState, popup){
      const width = frameState.size[0];
      const height = frameState.size[1];

      let center = toLonLat(frameState.viewState.center)
      let scale = Math.pow(2, 8 + frameState.viewState.zoom) / (2 * Math.PI)
      const angle = (-frameState.viewState.rotation * 180) / Math.PI;

      const d3Projection = d3.geoMercator()
        .scale(scale)
        .center(center)
        .translate([width / 2, height / 2])
        .angle(angle);

      const d3Path = d3.geoPath(d3Projection)

      // initialize
      this.svg.attr("width", width).attr("height", height);
      this.svg.selectAll("*").remove();


      // ------ From Observable Plot : https://github.com/observablehq/plot/blob/main/src/marks/arrow.js#L189

      let {getValue, scaleColor, scaleStroke, scaleCircle, filterFeatures, sortFeatures, limitFeatures} = this
      let {insetStart, insetEnd, headAngle, headLength, bend, sweep} = this.arrowOptions
      sweep = maybeSweep(sweep)

      // The angle between the arrow’s shaft and one of the wings; the “head”
      // angle between the wings is twice this value.
      const wingAngle = (headAngle * radians) / 2;

      // The length of the arrowhead’s “wings” (the line segments that extend from
      // the end point) relative to the stroke width.
      const wingScale = headLength / 1.5;

      this.svg.selectAll()
        .data(this.geojson.features.filter(filterFeatures).sort(sortFeatures).slice(0, limitFeatures))
        .join((enter) => {
          let g = enter.append('g')
          .attr("fill", "none")
          .attr("stroke-linecap", "round")
          .attr("stroke-linejoin", "round")

          g.append('path')
            .attr("d", (d) => {
              // The start ⟨x1,y1⟩ and end ⟨x2,y2⟩ points may be inset, and the
              // ending line angle may be altered for inset swoopy arrows.
              let p1 = d3Projection(d.geometry.coordinates[0])
              let p2 = d3Projection(d.geometry.coordinates[1])

              let x1 = p1[0], y1 = p1[1], x2 = p2[0], y2 = p2[1];
              if(x1 !== x2 | y2 !== y2){

                const lineLength = Math.hypot(x2 - x1, y2 - y1);
                if (lineLength <= insetStart + insetEnd) return null;
                let lineAngle = Math.atan2(y2 - y1, x2 - x1);

                // We don’t allow the wing length to be too large relative to the
                // length of the arrow. (Plot.vector allows arbitrarily large
                // wings, but that’s okay since vectors are usually small.)
                const headLength = Math.min(wingScale * scaleStroke(getValue(d)), lineLength / 3);

                // When bending, the offset between the straight line between the two points
                // and the outgoing tangent from the start point. (Also the negative
                // incoming tangent to the end point.) This must be within ±π/2. A positive
                // angle will produce a clockwise curve; a negative angle will produce a
                // counterclockwise curve; zero will produce a straight line.
                const bendAngle = sweep(x1, y1, x2, y2) * bend * radians;

                // The radius of the circle that intersects with the two endpoints
                // and has the specified bend angle.
                const r = Math.hypot(lineLength / Math.tan(bendAngle), lineLength) / 2;

                // Apply insets.
                if (insetStart || insetEnd) {
                  if (r < 1e5) {
                    // For inset swoopy arrows, compute the circle-circle
                    // intersection between a circle centered around the
                    // respective arrow endpoint and the center of the circle
                    // segment that forms the shaft of the arrow.
                    const sign = Math.sign(bendAngle);
                    const [cx, cy] = pointPointCenter([x1, y1], [x2, y2], r, sign);
                    if (insetStart) {
                      [x1, y1] = circleCircleIntersect([cx, cy, r], [x1, y1, insetStart], -sign * Math.sign(insetStart));
                    }
                    // For the end inset, rotate the arrowhead so that it aligns
                    // with the truncated end of the arrow. Since the arrow is a
                    // segment of the circle centered at ⟨cx,cy⟩, we can compute
                    // the angular difference to the new endpoint.
                    if (insetEnd) {
                      const [x, y] = circleCircleIntersect([cx, cy, r], [x2, y2, insetEnd], sign * Math.sign(insetEnd));
                      lineAngle += Math.atan2(y - cy, x - cx) - Math.atan2(y2 - cy, x2 - cx);
                      x2 = x
                      y2 = y
                    }
                  } else {
                    // For inset straight arrows, offset along the straight line.
                    const dx = x2 - x1,
                      dy = y2 - y1,
                      d = Math.hypot(dx, dy);
                    if (insetStart){
                      x1 += (dx / d) * insetStart
                      y1 += (dy / d) * insetStart
                    };
                    if (insetEnd){
                      x2 -= (dx / d) * insetEnd
                      y2 -= (dy / d) * insetEnd
                    };
                  }
                }

                // The angle of the arrow as it approaches the endpoint, and the
                // angles of the adjacent wings. Here “left” refers to if the
                // arrow is pointing up.
                const endAngle = lineAngle + bendAngle;
                const startAngle = lineAngle - bendAngle;

                const endLeftAngle = endAngle + wingAngle;
                const endRightAngle = endAngle - wingAngle;
                const startLeftAngle = startAngle + wingAngle;
                const startRightAngle = startAngle - wingAngle;

                // The endpoints of the two wings.
                const x3 = x2 - headLength * Math.cos(endLeftAngle);
                const y3 = y2 - headLength * Math.sin(endLeftAngle);
                const x4 = x2 - headLength * Math.cos(endRightAngle);
                const y4 = y2 - headLength * Math.sin(endRightAngle);

                // The endpoints of the two wings.
                const x5 = x1 + headLength * Math.cos(startLeftAngle);
                const y5 = y1 + headLength * Math.sin(startLeftAngle);
                const x6 = x1 + headLength * Math.cos(startRightAngle);
                const y6 = y1 + headLength * Math.sin(startRightAngle);

                // If the radius is very large (or even infinite, as when the bend
                // angle is zero), then render a straight line.
                const a = r < 1e5 ? `A${r},${r} 0,0,${bendAngle > 0 ? 1 : 0} ` : `L`;
                const h = headLength ? (this.bidirectionnal ? `M${x3},${y3}L${x2},${y2}L${x4},${y4}M${x5},${y5}L${x1},${y1}L${x6},${y6}` : `M${x3},${y3}L${x2},${y2}L${x4},${y4}`) : "";

                return `M${x1},${y1}${a}${x2},${y2}${h}`;
              } else {
                let r = scaleCircle(getValue(d))

                const headLength = wingScale * scaleStroke(getValue(d));

                // The angle of the arrow as it approaches the endpoint, and the
                // angles of the adjacent wings. Here “left” refers to if the
                // arrow is pointing up.
                const endAngle = 13 * Math.PI / 32;

                const leftAngle = endAngle + wingAngle * 1.3;
                const rightAngle = endAngle - wingAngle * 1.3;

                const startAngleC = Math.PI/6;
                const endAngleC = 2 * Math.PI;

                const x_start = x1 + r * Math.cos(startAngleC);
                const y_start = y1 + r * Math.sin(startAngleC);

                const x_end = x1 + r * Math.cos(endAngleC);
                const y_end = y1 + r * Math.sin(endAngleC);

                // The endpoints of the two wings.
                const x3 = x_end - headLength * Math.cos(leftAngle);
                const y3 = y_end - headLength * Math.sin(leftAngle);
                const x4 = x_end - headLength * Math.cos(rightAngle);
                const y4 = y_end - headLength * Math.sin(rightAngle);

                let path = d3.path()
                path.moveTo(x_start, y_start)
                path.arc(x1, y1, r, startAngleC, endAngleC);
                path.moveTo(x_end, y_end)
                path.lineTo(x3, y3)
                path.moveTo(x_end, y_end)
                path.lineTo(x4, y4)
                return path.toString();
              }
        })
            .attr("stroke", "white")
            .attr("stroke-width", (d) => scaleStroke(getValue(d)) + 1)
            .style("pointer-events", "stroke");

          g.append('path')
            .attr("d", (d) => {
              // The start ⟨x1,y1⟩ and end ⟨x2,y2⟩ points may be inset, and the
              // ending line angle may be altered for inset swoopy arrows.
              let p1 = d3Projection(d.geometry.coordinates[0])
              let p2 = d3Projection(d.geometry.coordinates[1])

              let x1 = p1[0], y1 = p1[1], x2 = p2[0], y2 = p2[1];
              if(x1 !== x2 | y2 !== y2){

                const lineLength = Math.hypot(x2 - x1, y2 - y1);
                if (lineLength <= insetStart + insetEnd) return null;
                let lineAngle = Math.atan2(y2 - y1, x2 - x1);

                // We don’t allow the wing length to be too large relative to the
                // length of the arrow. (Plot.vector allows arbitrarily large
                // wings, but that’s okay since vectors are usually small.)
                const headLength = Math.min(wingScale * scaleStroke(getValue(d)), lineLength / 3);

                // When bending, the offset between the straight line between the two points
                // and the outgoing tangent from the start point. (Also the negative
                // incoming tangent to the end point.) This must be within ±π/2. A positive
                // angle will produce a clockwise curve; a negative angle will produce a
                // counterclockwise curve; zero will produce a straight line.
                const bendAngle = sweep(x1, y1, x2, y2) * bend * radians;

                // The radius of the circle that intersects with the two endpoints
                // and has the specified bend angle.
                const r = Math.hypot(lineLength / Math.tan(bendAngle), lineLength) / 2;

                // Apply insets.
                if (insetStart || insetEnd) {
                  if (r < 1e5) {
                    // For inset swoopy arrows, compute the circle-circle
                    // intersection between a circle centered around the
                    // respective arrow endpoint and the center of the circle
                    // segment that forms the shaft of the arrow.
                    const sign = Math.sign(bendAngle);
                    const [cx, cy] = pointPointCenter([x1, y1], [x2, y2], r, sign);
                    if (insetStart) {
                      [x1, y1] = circleCircleIntersect([cx, cy, r], [x1, y1, insetStart], -sign * Math.sign(insetStart));
                    }
                    // For the end inset, rotate the arrowhead so that it aligns
                    // with the truncated end of the arrow. Since the arrow is a
                    // segment of the circle centered at ⟨cx,cy⟩, we can compute
                    // the angular difference to the new endpoint.
                    if (insetEnd) {
                      const [x, y] = circleCircleIntersect([cx, cy, r], [x2, y2, insetEnd], sign * Math.sign(insetEnd));
                      lineAngle += Math.atan2(y - cy, x - cx) - Math.atan2(y2 - cy, x2 - cx);
                      x2 = x
                      y2 = y
                    }
                  } else {
                    // For inset straight arrows, offset along the straight line.
                    const dx = x2 - x1,
                      dy = y2 - y1,
                      d = Math.hypot(dx, dy);
                    if (insetStart){
                      x1 += (dx / d) * insetStart
                      y1 += (dy / d) * insetStart
                    };
                    if (insetEnd){
                      x2 -= (dx / d) * insetEnd
                      y2 -= (dy / d) * insetEnd
                    };
                  }
                }

                // The angle of the arrow as it approaches the endpoint, and the
                // angles of the adjacent wings. Here “left” refers to if the
                // arrow is pointing up.
                const endAngle = lineAngle + bendAngle;
                const startAngle = lineAngle - bendAngle;

                const endLeftAngle = endAngle + wingAngle;
                const endRightAngle = endAngle - wingAngle;
                const startLeftAngle = startAngle + wingAngle;
                const startRightAngle = startAngle - wingAngle;

                // The endpoints of the two wings.
                const x3 = x2 - headLength * Math.cos(endLeftAngle);
                const y3 = y2 - headLength * Math.sin(endLeftAngle);
                const x4 = x2 - headLength * Math.cos(endRightAngle);
                const y4 = y2 - headLength * Math.sin(endRightAngle);

                // The endpoints of the two wings.
                const x5 = x1 + headLength * Math.cos(startLeftAngle);
                const y5 = y1 + headLength * Math.sin(startLeftAngle);
                const x6 = x1 + headLength * Math.cos(startRightAngle);
                const y6 = y1 + headLength * Math.sin(startRightAngle);

                // If the radius is very large (or even infinite, as when the bend
                // angle is zero), then render a straight line.
                const a = r < 1e5 ? `A${r},${r} 0,0,${bendAngle > 0 ? 1 : 0} ` : `L`;
                const h = headLength ? (this.bidirectionnal ? `M${x3},${y3}L${x2},${y2}L${x4},${y4}M${x5},${y5}L${x1},${y1}L${x6},${y6}` : `M${x3},${y3}L${x2},${y2}L${x4},${y4}`) : "";

                return `M${x1},${y1}${a}${x2},${y2}${h}`;
              } else {
                let r = scaleCircle(getValue(d))

                const headLength = wingScale * scaleStroke(getValue(d));

                // The angle of the arrow as it approaches the endpoint, and the
                // angles of the adjacent wings. Here “left” refers to if the
                // arrow is pointing up.
                const endAngle = 13 * Math.PI / 32;

                const leftAngle = endAngle + wingAngle * 1.3;
                const rightAngle = endAngle - wingAngle * 1.3;

                const startAngleC = Math.PI/6;
                const endAngleC = 2 * Math.PI;

                const x_start = x1 + r * Math.cos(startAngleC);
                const y_start = y1 + r * Math.sin(startAngleC);

                const x_end = x1 + r * Math.cos(endAngleC);
                const y_end = y1 + r * Math.sin(endAngleC);

                // The endpoints of the two wings.
                const x3 = x_end - headLength * Math.cos(leftAngle);
                const y3 = y_end - headLength * Math.sin(leftAngle);
                const x4 = x_end - headLength * Math.cos(rightAngle);
                const y4 = y_end - headLength * Math.sin(rightAngle);

                let path = d3.path()
                path.moveTo(x_start, y_start)
                path.arc(x1, y1, r, startAngleC, endAngleC);
                path.moveTo(x_end, y_end)
                path.lineTo(x3, y3)
                path.moveTo(x_end, y_end)
                path.lineTo(x4, y4)
                return path.toString();
              }
        })
            .attr("stroke", (d) => scaleColor(getValue(d)))
            .attr("stroke-width", (d) => scaleStroke(getValue(d)))
            .style("pointer-events", "stroke");
    })
  }




    addHover(popup) {
      function onMouseMove(e){
        e.currentTarget.popup.show(e, `${e.currentTarget.label}`);
      }
      function onMouseOut(e){
        popup.hide()
      }

      this.svg
        .selectAll("g")
        .nodes()
        .forEach((item, i) => {
          item.label = this.allLabels[i]
          item.popup = popup
          item.addEventListener("mousemove", onMouseMove)
        });

      this.svg.selectAll("g").on("mouseout", onMouseOut);
    }
  }



  const constant = (x) => () => x;
  // Validates the specified required string against the allowed list of keywords.
  function keyword(input, name, allowed) {
    const i = `${input}`.toLowerCase();
    if (!allowed.includes(i)) throw new Error(`invalid ${name}: ${input}`);
    return i;
  }

  // Maybe flip the bend angle, depending on the arrow orientation.
  function maybeSweep(sweep = 1) {
    if (typeof sweep === "number") {return constant(Math.sign(sweep))};
    if (typeof sweep === "function") {return (x1, y1, x2, y2) => Math.sign(sweep(x1, y1, x2, y2))};
    switch (keyword(sweep, "sweep", ["+x", "-x", "+y", "-y"])) {
      case "+x":
        return (x1, y1, x2) => ascending(x1, x2);
      case "-x":
        return (x1, y1, x2) => descending(x1, x2);
      case "+y":
        return (x1, y1, x2, y2) => ascending(y1, y2);
      case "-y":
        return (x1, y1, x2, y2) => descending(y1, y2);
    }
  }

  // Returns the center of a circle that goes through the two given points ⟨ax,ay⟩
  // and ⟨bx,by⟩ and has radius r. There are two such points; use the sign +1 or
  // -1 to choose between them. Returns [NaN, NaN] if r is too small.
  function pointPointCenter([ax, ay], [bx, by], r, sign) {
    const dx = bx - ax,
      dy = by - ay,
      d = Math.hypot(dx, dy);
    const k = (sign * Math.sqrt(r * r - (d * d) / 4)) / d;
    return [(ax + bx) / 2 - dy * k, (ay + by) / 2 + dx * k];
  }

  // Given two circles, one centered at ⟨ax,ay⟩ with radius ar, and the other
  // centered at ⟨bx,by⟩ with radius br, returns a point at which the two circles
  // intersect. There are typically two such points; use the sign +1 or -1 to
  // chose between them. Returns [NaN, NaN] if there is no intersection.
  // https://mathworld.wolfram.com/Circle-CircleIntersection.html
  function circleCircleIntersect([ax, ay, ar], [bx, by, br], sign) {
    const dx = bx - ax,
      dy = by - ay,
      d = Math.hypot(dx, dy);
    const x = (dx * dx + dy * dy - br * br + ar * ar) / (2 * d);
    const y = sign * Math.sqrt(ar * ar - x * x);
    return [ax + (dx * x + dy * y) / d, ay + (dy * x - dx * y) / d];
  }
