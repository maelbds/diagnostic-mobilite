import * as d3 from "d3";



// to display figures properly
export function formatFigure(figure, significant_digits=null, simplify_figure_inf1=true){
  if (typeof(figure) == "number"){
    if (significant_digits == null){
      return figure.toLocaleString("fr-FR")
    } else {
      if (figure < 1 && simplify_figure_inf1){
        return parseFloat(figure.toPrecision(1)).toLocaleString("fr-FR")
      } else {
        return parseFloat(figure.toPrecision(significant_digits)).toLocaleString("fr-FR")
      }
    }
  }
  else{
    return figure
  }
}

// to display names properly : return string with capital letter for first letter of each word
export function titleCase(str) {
  if (str==null){return str}
   var splitStr = str.toLowerCase().split(' ');
   for (var i = 0; i < splitStr.length; i++) {
       // You do not need to check if i is larger than splitStr length, as your for does that for you
       // Assign it back to the array
       splitStr[i] = splitStr[i].charAt(0).toUpperCase() + splitStr[i].substring(1);
   }
   // Directly return the joined string
   return splitStr.join(' ');
}

export function downloadBlob(content, filename, contentType){
  // Create a blob
  let blob = new Blob([content], { type: contentType });
  let url = URL.createObjectURL(blob);

  // Create a link to download it
  let a = document.createElement('a');
  a.href = url;
  a.setAttribute('download', filename);
  a.click();
}

export function arrayToCsv(array){
  let csvFormat = array.map(row =>
    row
    .join(';')  // comma-separated
  ).join('\r\n');  // rows starting on new lines
  return csvFormat
}

export function cols_to_rows(cols){
    let rows = [];
    for (let i=0; i<cols[0].length; i++){
      rows.push(cols.map((t) => t[i]))
    }
    return rows
}

export function downloadCSV(headlines, rows, format_csv, name){
  let format_rows = rows.map((row) => row.map((e, i)=> format_csv[i](e)))
  let all_rows = [headlines].concat(format_rows)
  let csv = arrayToCsv(all_rows)
  downloadBlob("\uFEFF" + csv, name + ".csv", "text/csv;charset=utf-8,")
}


export function downloadGeoJson(geojson, name){
  downloadBlob(JSON.stringify(geojson), name + ".json", "application/json;charset=utf-8,")
}



// ---------------- download map image as png ------------------------------

const xmlns = "http://www.w3.org/2000/xmlns/";
const xlinkns = "http://www.w3.org/1999/xlink";
const svgns = "http://www.w3.org/2000/svg";

// ------- shorthand to set canvas and get context
function context2d(canvas, width, height, dpi=null) {
  if (dpi == null) dpi = window.devicePixelRatio;
  canvas.width = width * dpi;
  canvas.height = height * dpi;
  canvas.style.width = width + "px";
  var context = canvas.getContext("2d");
  context.scale(dpi, dpi);
  return context;
}

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

export function downloadSVGImage(svg, filename){
  console.log(svg)
  let all_layers = [svg]
  let width = 1500;
  let height = svg.getBoundingClientRect().height/svg.getBoundingClientRect().width * width;
  console.log(svg.getBoundingClientRect())
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







export function initTable(objects){
  let elements = objects.mesh_elements_geojson.features.map((f) => f.properties);

  let headlines = ["Code INSEE", "Nom"]
  let cols=[elements.map((c)=> c.geo_code), elements.map((c)=> c.name)]
  let format_table=[(f)=>f, (f)=>f]
  let format_csv=[(f)=>f, (f)=>f]
  let align=["l", "l"]

  let rows = cols_to_rows(cols).sort((a, b)=> ('' + a[1]).localeCompare(b[1])) // tri par ordre alphabétique des noms de commune

  return {headlines, rows, align, format_table, format_csv}
}


export function objectsEquals(o1, o2){
  return Object.keys(o1).every(k1 => Object.keys(o2).includes(k1) && o1[k1] === o2[k1])
}


export function setCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}
export function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}
export function eraseCookie(name) {
    document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}
