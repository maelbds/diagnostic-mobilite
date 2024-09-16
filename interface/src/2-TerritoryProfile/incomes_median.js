import {ChoroLayer} from '../i-Map/Layers/ChoroLayer';

import {c_gradient_reds_greens} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';


function getChoroLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects

  let value = (e) => e["Q2"] === null ? null : Math.round(e["Q2"]/12)
  let is_available = (e) => e["Q2"] !== null

  let choro_legend = {
    thresholds: [900, 1650, 1750, 1830, 1950, 2050, 4500],
    colors: c_gradient_reds_greens.slice(2, 8),
    references: [
      {label: "Département", value: mesh_elements_ref.dep === null ? "indisponible" : formatFigure(value(mesh_elements_ref.dep))},
      {label: "France", value: formatFigure(value(mesh_elements_ref.france))},
    ],
    title: `Niveau de vie médian`,
    unit: "€/uc/mois",
    format: (d) => formatFigure(d)
  }

  let choro_layer = new ChoroLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => value(d),
    getLabel: (d) => is_available(d) ? `<b>${formatFigure(value(d))}</b> €/mois/uc` : "<i>donnée indisponible</i>",
    legend: choro_legend
  });

  return [choro_layer]
}


function getMeshElementsTable(objects, selected_filters){
  let headlines = [], cols = [], format_table = [], format_csv = [], align = [];
  let mesh_elements = objects.mesh_elements_geojson.features.map((f) => f.properties)

  let value = (e) => e["Q2"] === null ? null : Math.round(e["Q2"]/12)

  headlines.push("Niveau de vie médian")
  cols.push(mesh_elements.map((c)=> value(c)))
  format_table.push((f)=>formatFigure(f))
  format_csv.push((f)=>f)
  align.push("r")

  return {headlines, cols, format_table, format_csv, align}
}


export const incomes_median = new Indicator({
    indicator: "incomes_median",
    label: "niveau de vie médian",
    data_source: "verified",
    description: "Le niveau de vie est égal au revenu disponible du ménage divisé par le nombre d'unités de consommation (uc). Il est ici calculé sur le revenu disponible qui correspond aux revenus auxquels il faut ajouter les prestations sociales et retirer les impôts directs.",

    tables: {
      mesh: getMeshElementsTable
    },
    layers : {
      choropleth: getChoroLayer
    },
    datasets_names: ["territory/incomes"]
})
