import {ChoroLayer} from '../i-Map/Layers/ChoroLayer';

import {c_gradient_greens, c_yellow} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';


function getChoroLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects

  let value = (e) => e.motorisation_rate
  let is_available = (e) => e.motorisation_rate !== null

  let choro_legend = {
    thresholds: objects.mesh_elements_leg.motorisation_rate,
    colors: c_gradient_greens,
    references: [
      {label: "Territoire", value: formatFigure(value(mesh_elements_ref.territory))},
      {label: "Département", value: formatFigure(value(mesh_elements_ref.dep))},
      {label: "France", value: formatFigure(value(mesh_elements_ref.france))},
    ],
    title: `Part des ménages disposant d'au moins un véhicule`,
    unit: "%",
    format: (d) => formatFigure(d)
  }

  let choro_layer = new ChoroLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => value(d),
    getLabel: (d) => is_available(d) ? `<b>${formatFigure(value(d))} %</b> des ménages disposent d'au moins un véhicule` : "<i>donnée indisponible</i>",
    legend: choro_legend
  });

  return [choro_layer]
}


function getMeshElementsTable(objects, selected_filters){
  let headlines = [], cols = [], format_table = [], format_csv = [], align = [];
  let mesh_elements = objects.mesh_elements_geojson.features.map((f) => f.properties)

  headlines.push("Part des ménages disposant d'au moins un véhicule")
  cols.push(mesh_elements.map((c)=> c.motorisation_rate))
  format_table.push((f)=>formatFigure(f))
  format_csv.push((f)=>f)
  align.push("r")

  return {headlines, cols, format_table, format_csv, align}
}


export const households_motorisation = new Indicator({
    indicator: "households_motorisation",
    label: "équipement automobile des ménages",
    data_source: "verified",

    filters: [],

    tables: {
      mesh: getMeshElementsTable
    },
    layers : {
      choropleth: getChoroLayer
    },
    datasets_names: ["offer/households_motorisation"]
})
