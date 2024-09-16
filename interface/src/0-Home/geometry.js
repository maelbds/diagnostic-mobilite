import * as topojson from "topojson";
import * as d3 from "d3";

import {enrichGeojson} from '../f-Utilities/data_handling';

export function computeGeometry(topo, geography, communes_attr, epci_attr){
  let com_codes = geography.com.map((c) => c.geo_code)
  let epci_codes = [...new Set(geography.com.map((c) => c.epci))]

  // communes
  let com_mesh_lines = topojson.mesh(topo, topo.objects.com, (a, b) => com_codes.includes(a.properties.codgeo) && com_codes.includes(b.properties.codgeo) && a!==b)
  let com_mesh_outline = topojson.merge(topo, topo.objects.com.geometries.filter((o) => com_codes.includes(o.properties.codgeo)))

  let com_mesh = topojson.feature(topo, {type: "GeometryCollection", geometries: topo.objects.com.geometries.filter((o) => com_codes.includes(o.properties.codgeo))})
  com_mesh = enrichGeojson(com_mesh, geography.com)

  // epci
  let epci_mesh_lines_geometries = epci_codes.map((c) => [c, topojson.mergeArcs(topo, topo.objects.com.geometries.filter((o) => c === communes_attr.get(o.properties.codgeo).epci))])
                                              .map(d => ({type:d[1].type, properties:{codgeo: d[0]}, arcs:d[1].arcs}))
  let epci_mesh_lines = topojson.mesh(topo, {type: "GeometryCollection", geometries: epci_mesh_lines_geometries}, (a, b) => a !== b)

  let epci_mesh_outline = topojson.merge(topo, topo.objects.com.geometries.filter((o) => epci_codes.includes(communes_attr.get(o.properties.codgeo).epci)))

  let epci_mesh_features = epci_codes.map((c) => [c, topojson.merge(topo, topo.objects.com.geometries.filter((o) => c === communes_attr.get(o.properties.codgeo).epci))])
                                    .map(d => ({type:'Feature', properties:{codgeo: d[0], center: d3.geoCentroid(d[1]), libgeo: epci_attr.get(d[0]).epci_name}, geometry:d[1]}))
  let epci_mesh = {type: "FeatureCollection", features: epci_mesh_features}
  epci_mesh = enrichGeojson(epci_mesh, geography.epci)


  let geometry = {
    com: {
      mesh_lines: com_mesh_lines,
      mesh_outline: com_mesh_outline,
      mesh: com_mesh
    },
    epci: {
      mesh_lines: epci_mesh_lines,
      mesh_outline: epci_mesh_outline,
      mesh: epci_mesh
    },
    perimeter: com_mesh_outline,
  }

  return geometry
}
