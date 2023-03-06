import React, { Component } from 'react';
import {c_gradient_reds_greens, c_yellow, c_missing_data} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func'

import {getLegendMode} from '../b-LeafletMap/leaflet_map';
import {createCommunesMassLayer, createCommunesLayer} from '../b-LeafletMap/LeafletMapElement/createCommune'
import {createPointsMassLayer} from '../b-LeafletMap/LeafletMapElement/createPoint'

export function getWorkPlaceElements(communes, areas_by_reason){
    let communes_coords = communes.map((c) => c.center);
    let communes_names = communes.map((c) => c.name);

    // WORK AREAS
    var work_areas = areas_by_reason.filter((abr)=>abr["name"]=="work")[0]["areas"];
    work_areas = work_areas.filter((wa)=> communes_names.includes(wa.name))
    let work_areas_sorted = work_areas.sort((a, b)=> b.mass - a.mass)
    var work_areas_coords = work_areas_sorted.map((a) => a.coords)
    var work_areas_masses = work_areas_sorted.map((a) => a.mass)
    var work_areas_labels = work_areas_sorted.map((a) => '<b>' + a.name + "</b></br>" + formatFigure(a.mass) + " emplois")

    // Communes
    let communes_wd = communes.filter((c) => work_areas.filter((wa)=>wa.name==c.name)[0].mass != null)

    let communes_masses = communes_wd.map((c) => Math.round(work_areas.filter((wa)=>wa.name==c.name)[0].mass/c.status.employed*100));
    let communes_labels = communes_wd.map((c) => "<b>" + c.name + "</b></br>" + formatFigure(c.status.employed) + " actifs - " +
                                                formatFigure(work_areas.filter((wa)=>wa.name==c.name)[0].mass) + " emplois</br>" +
                                              "Ratio emploi/actif.ves : " + Math.round(work_areas.filter((wa)=>wa.name==c.name)[0].mass/c.status.employed*100) + "%");

    let communes_nd = communes.filter((c) => work_areas.filter((wa)=>wa.name==c.name)[0].mass == null)
    let communes_nd_labels = communes_nd.map((c) => c.name);


    let mode = "work_ratio"
    let legend_label = "Ratio emploi/actif.ves"
    let legend_label_2 = "Nombre d'emplois dans la commune"
    let legend_unit = "(%)"
    let colors = c_gradient_reds_greens.slice(2, 8)
    let color = c_yellow
    let sources = ["dossier_complet"]

    let legend_values = communes_masses
    let missing_data = communes_nd.length > 0

    // --- create layers
    let communes_layer = createCommunesMassLayer(communes_wd, communes_masses, communes_labels, mode, colors);
    let communes_layer_nd = createCommunesLayer(communes_nd, communes_nd_labels, c_missing_data);
    let work_layer = createPointsMassLayer(work_areas_coords, work_areas_masses, work_areas_labels, color);

    let [legend_intervals, legend_colors] = getLegendMode(mode, legend_values, colors)
    let legend = [
      {type: "LegendLabel", params: {label: legend_label, unit: legend_unit}},
      {type: "LegendValues", params: {intervals: legend_intervals, colors: legend_colors, missing_data: missing_data}},
      {type: "LegendSpace", params: {}},
      {type: "LegendPointMass", params: {label: legend_label_2, unit: null, color: color}}
    ]

    let layer_to_fit = communes_layer.addLayer(communes_layer_nd)
    let layers = [communes_layer, communes_layer_nd, work_layer]

    return {layer_to_fit, layers, legend, sources}
}


export function getWorkPlaceElementsTable(communes, areas_by_reason){
  // WORK AREAS
  let work_areas = areas_by_reason.filter((abr)=>abr["name"]=="work")[0]["areas"];
  communes.map((c) => c.jobs = work_areas.filter((wa)=>wa.name==c.name)[0].mass);

  var headlines=["Code Insee", "Commune", "Nombre d'emplois", "Population active", "Ratio emploi/population active (%)"]
  var cols=[communes.map((c)=> c.geo_code),
            communes.map((c)=> c.name),
            communes.map((c)=> c.jobs != null ? c.jobs : null),
            communes.map((c)=> c.status.employed != null ? c.status.employed : null),
            communes.map((c)=> c.jobs != null ? c.status.employed != null ? Math.round(c.jobs/c.status.employed*100) : null : null)]
  var format_table=[(f)=>f,
              (f)=>f,
              (f)=>formatFigure(f),
              (f)=>formatFigure(f),
              (f)=>f]
  var format_csv=[(f)=>f,
              (f)=>f,
              (f)=>f,
              (f)=>f,
              (f)=>formatFigure(f,3, false)]
  var align=["l", "l", "r", "r", "r"]

  var rows = cols_to_rows(cols)
  var sources_table = ["dossier_complet"]
  var name_csv= "emplois"
  return {headlines, rows, align, format_table, format_csv, sources_table, name_csv}
}
