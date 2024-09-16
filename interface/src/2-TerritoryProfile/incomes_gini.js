import {ChoroLayer} from '../i-Map/Layers/ChoroLayer';

import {c_gradient_reds_greens} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';


function getChoroLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects

  let value = (e) => e["GI"] === null ? null : Math.round(e["GI"]*100)/100
  let is_available = (e) => e["GI"] !== null

  let choro_legend = {
    thresholds: [0, 0.23, 0.26, 0.29, 0.32, 0.35, 1],
    colors: c_gradient_reds_greens.slice(2, 8).reverse(),
    references: [
      {label: "Département", value: mesh_elements_ref.dep === null ? "indisponible" : formatFigure(value(mesh_elements_ref.dep))},
      {label: "France", value: formatFigure(value(mesh_elements_ref.france))},
    ],
    title: `Indice de Gini`,
    unit: "",
    format: (d) => formatFigure(d)
  }

  let choro_layer = new ChoroLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => value(d),
    getLabel: (d) => is_available(d) ? `Indice de Gini : <b>${formatFigure(value(d))}</b>` : "<i>donnée indisponible</i>",
    legend: choro_legend
  });

  return [choro_layer]
}


function getMeshElementsTable(objects, selected_filters){
  let headlines = [], cols = [], format_table = [], format_csv = [], align = [];
  let mesh_elements = objects.mesh_elements_geojson.features.map((f) => f.properties)

  let value = (e) => e["GI"] === null ? null : Math.round(e["GI"]*100)/100

  headlines.push("Indice de Gini")
  cols.push(mesh_elements.map((c)=> value(c)))
  format_table.push((f)=>formatFigure(f))
  format_csv.push((f)=>formatFigure(f))
  align.push("r")

  return {headlines, cols, format_table, format_csv, align}
}


export const incomes_gini = new Indicator({
    indicator: "incomes_gini",
    label: "indice de Gini",
    data_source: "verified",
    description: "L’indice de Gini traduit une inégalité globale, le rapport interdécile une inégalité ponctuelle. Plus il est proche de 1, plus nous sommes dans une société inégalitaire et plus il est proche de zéro, plus nous sommes dans une société égalitaire.",

    tables: {
      mesh: getMeshElementsTable
    },
    layers : {
      choropleth: getChoroLayer
    },
    datasets_names: ["territory/incomes"]
})
