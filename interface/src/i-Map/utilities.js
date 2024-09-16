import * as d3 from "d3";


// ------- shorthand to set canvas and get context
export function context2d(canvas, width, height, dpi=null) {
  if (dpi == null) dpi = window.devicePixelRatio;
  canvas.width = width * dpi;
  canvas.height = height * dpi;
  canvas.style.width = width + "px";
  var context = canvas.getContext("2d");
  context.scale(dpi, dpi);
  return context;
}

// --------- delaunay used on mesh hover
export function delaunay_nextring(delaunay, current_ring, kernel){
  if (!kernel) kernel = []
  let nextring = current_ring.flatMap((d,i,self) => [...delaunay.neighbors(d)].filter(e => !self.includes(e) && !kernel.includes(e)) )
  return [...new Set(nextring)]
}



// ---------------- download map image as png ------------------------------

const xmlns = "http://www.w3.org/2000/xmlns/";
const xlinkns = "http://www.w3.org/1999/xlink";
const svgns = "http://www.w3.org/2000/svg";

function serialize(svg) {
  svg = svg.cloneNode(true);
  const fragment = window.location.href + "#";
  const walker = document.createTreeWalker(svg, NodeFilter.SHOW_ELEMENT);
  while (walker.nextNode()) {
    for (const attr of walker.currentNode.attributes) {
      if (attr.value.includes(fragment)) {
        attr.value = attr.value.replace(fragment, "#");
      }
    }
  }
  svg.setAttributeNS(xmlns, "xmlns", svgns);
  svg.setAttributeNS(xmlns, "xmlns:xlink", xlinkns);
  const serializer = new window.XMLSerializer;
  const string = serializer.serializeToString(svg);
  return new Blob([string], {type: "image/svg+xml"});
};

export function downloadMapImage(map, filename){
  let all_layers = Array.from(map.getViewport().querySelectorAll(".ol-layer canvas, canvas.ol-layer, .ol-layers svg"))
  let width = all_layers[0].width,
      height = all_layers[0].height
  let canvas_to_download = d3.create("canvas").attr("width", width).attr("height", height).node();
  let context = canvas_to_download.getContext("2d");

  let all_promises = []

  all_layers.forEach((layer, i) => {
    if(layer instanceof SVGElement){
      all_promises.push(new Promise((res, err) => {
        const image = new Image;
        image.onerror = err;
        image.onload = () => res(image);
        image.src = URL.createObjectURL(serialize(layer));
      }))
    } else {
      all_promises.push(new Promise((res, err) => res(layer)))
    }
  });

  Promise.all(all_promises).then((res)=>{
    res.forEach((l) => {
      context.drawImage(l, 0, 0, width, height)
    });

    let url = canvas_to_download.toDataURL("image/png")

    // Create a link to download it
    let a = document.createElement('a');
    a.href = url;
    a.setAttribute('download', filename);
    a.click();

  })
}

// --------------------- to display long text with svg - used in Legend
// from https://gist.github.com/mbostock/7555321
export function wrap(text, width) {
  text.each(function() {
    var text = d3.select(this),
        words = text.text().split(/\s+/).reverse(),
        word,
        line = [],
        lineNumber = 0,
        lineHeight = 1.1, // ems
        x = text.attr("x"),
        y = text.attr("y"),
        dy = text.attr("dy") === null ? 0 : parseFloat(text.attr("dy")),
        tspan = text.text(null).append("tspan")
        //.attr('alignment-baseline', 'hanging')
        .attr("x", x).attr("y", y).attr("dy", dy + "em");
    while (word = words.pop()) {
      line.push(word);
      tspan.text(line.join(" "));
      if (tspan.node().getBBox().width > width) {
        line.pop();
        tspan.text(line.join(" "));
        line = [word];
        tspan = text.append("tspan")
        //.attr('alignment-baseline', 'hanging')
        .attr("x", x).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
      }
    }
  });
}
