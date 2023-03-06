import * as d3 from "d3";


export function context2d(canvas, width, height, dpi=null) {
  if (dpi == null) dpi = window.devicePixelRatio;
  canvas.width = width * dpi;
  canvas.height = height * dpi;
  canvas.style.width = width + "px";
  var context = canvas.getContext("2d");
  context.scale(dpi, dpi);
  return context;
}


export function delaunay_nextring(delaunay, current_ring, kernel){
    if (!kernel) kernel = []
    let nextring = current_ring.flatMap((d,i,self) =>
                                  [...delaunay.neighbors(d)].filter(e => !self.includes(e) && !kernel.includes(e)) )
    return [...new Set(nextring)]
  }


export function createStripeDiagonalPatternCanvas(){
  // Create a pattern, offscreen
  const patternCanvas = document.createElement('canvas');
  const patternContext = patternCanvas.getContext('2d');

  // Give the pattern a width and height of 50
  patternCanvas.width = 50;
  patternCanvas.height = 50;

  let range = 10

  // Give the pattern a background color and draw an arc
  patternContext.beginPath()
  patternContext.strokeStyle = "black";
  patternContext.lineWidth = 1;
  patternContext.lineCap = "butt";
  for (var i=1; i<(50/range*2); i++){
    patternContext.moveTo(0, i*range)
    patternContext.lineTo(i*range, 0);
  }
  patternContext.stroke();

  return patternCanvas
}


export function createStripePatternCanvas(angle, strokeWidth, color){
  // Create a pattern, offscreen
  const patternCanvas = document.createElement('canvas');
  const patternContext = patternCanvas.getContext('2d');

  // Give the pattern a width and height of 50
  patternCanvas.width = 50;
  patternCanvas.height = 50;

  patternContext.rotate(Math.PI/4*angle)

  let range = 50 / 5
  if(angle == 1) range = 50 / Math.sqrt(2) / 3

  // Give the pattern a background color and draw an arc
  patternContext.beginPath()
  patternContext.strokeStyle = color;
  patternContext.lineWidth = strokeWidth;
  patternContext.lineCap = "butt";
  for (var i=0; i<(50/range * 2); i++){
    patternContext.moveTo(0, -50+1.5+i*range)
    patternContext.lineTo(100, -50+1.5 +i*range);
  }
  patternContext.stroke();

  return patternCanvas
}

export function createDottedPatternCanvas(){
  // Create a pattern, offscreen
  const patternCanvas = document.createElement('canvas');
  const patternContext = patternCanvas.getContext('2d');

  // Give the pattern a width and height
  patternCanvas.width = 40;
  patternCanvas.height = 40;

  patternContext.scale(2, 2)

  // Give the pattern a background color and draw an arc
  patternContext.beginPath()
  patternContext.fillStyle = "rgba(0, 0, 0, 0.6)";
  patternContext.arc(5, 5, 1.5, 0, 2*Math.PI)
  patternContext.arc(15, 15, 1.5, 0, 2*Math.PI)
  patternContext.fill();

  return patternCanvas
}

export function hoverInfo(name_commune, code_commune, name_aav, name_typo_aav, name_epci=null){
  let aav
  if(name_typo_aav == "") aav = name_aav
  else aav = name_typo_aav + " - " + name_aav

  if (name_epci == null) return `<p class="mb-2"><b>${name_commune}</b> (${code_commune})</p>
         <p>${aav}</p>`
  else return `<p class="mb-2"><b>${name_commune}</b> (${code_commune})</p>
         <p class="mb-1">${name_epci}</p>
         <p>${aav}</p>`
}
