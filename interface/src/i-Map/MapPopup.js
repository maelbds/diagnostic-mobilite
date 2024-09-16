import * as d3 from "d3";


export class MapPopup{
  constructor(map){
    this.map_dom_element = map.targetElement_
    this.popup = d3.select(this.map_dom_element).append("div")
    .attr("class", "popup")
    .style("position", "absolute")
    .style("display", "none")

    this.popup.on("mouseover", ()=>{
      this.hide()
    })

    this.margin = 10
  }

  show(e, content){
    this.popup.style("display", "block")
    this.popup.html(`<p>${content}</p>`)

    let m = this.margin,
        w = this.popup.node().offsetWidth,
        h = this.popup.node().offsetHeight;

    let width_c = this.map_dom_element.offsetWidth - 220

    if (e.offsetY < h + m){
      this.popup.attr("class", "popup downside")
    } else {
      this.popup.attr("class", "popup upside")
    }

    this.popup.style("top", e.offsetY + "px")
    this.popup.style("left", Math.max(w/2 + m, Math.min(e.offsetX, width_c - w/2 - m)) + "px")
  }

  hide(){
    this.popup.style("display", "none")
  }
}
