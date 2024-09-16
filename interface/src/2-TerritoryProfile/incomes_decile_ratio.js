import {ChoroLayer} from '../i-Map/Layers/ChoroLayer';

import {c_gradient_reds_greens} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';


function getChoroLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects

  let value = (e) => e["RD"] === null ? null : Math.round(e["RD"]*10)/10
  let is_available = (e) => e["RD"] !== null

  let choro_legend = {
    thresholds: [1, 2.6, 3, 3.4, 3.8, 4.2, 15],
    colors: c_gradient_reds_greens.slice(2, 8).reverse(),
    references: [
      {label: "Département", value: mesh_elements_ref.dep === null ? "indisponible" : formatFigure(value(mesh_elements_ref.dep))},
      {label: "France", value: formatFigure(value(mesh_elements_ref.france))},
    ],
    title: `Écart interdécile`,
    unit: "",
    format: (d) => formatFigure(d)
  }

  let choro_layer = new ChoroLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => value(d),
    getLabel: (d) => is_available(d) ? `Écart interdécile : <b>${formatFigure(value(d))}</b>` : "<i>donnée indisponible</i>",
    legend: choro_legend
  });

  return [choro_layer]
}


function getMeshElementsTable(objects, selected_filters){
  let headlines = [], cols = [], format_table = [], format_csv = [], align = [];
  let mesh_elements = objects.mesh_elements_geojson.features.map((f) => f.properties)

  let value = (e) => e["RD"] === null ? null : Math.round(e["RD"]*10)/10

  headlines.push("Écart interdécile")
  cols.push(mesh_elements.map((c)=> value(c)))
  format_table.push((f)=>formatFigure(f))
  format_csv.push((f)=>formatFigure(f))
  align.push("r")

  return {headlines, cols, format_table, format_csv, align}
}


export const incomes_decile_ratio = new Indicator({
    indicator: "incomes_decile_ratio",
    label: "écart interdécile",
    data_source: "verified",
    description: "L'écart interdécile est le rapport entre le revenu des 10% les plus riches et celui des 10% les plus pauvres. Il traduit les inégalités ponctuelles",

    tables: {
      mesh: getMeshElementsTable
    },
    layers : {
      choropleth: getChoroLayer
    },
    datasets_names: ["territory/incomes"]
})
