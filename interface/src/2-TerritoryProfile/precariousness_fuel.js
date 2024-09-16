import {ChoroLayer} from '../i-Map/Layers/ChoroLayer';

import {c_gradient_reds_greens} from '../a-Graphic/Colors';
import {formatFigure, cols_to_rows} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';


function getChoroLayer(objects, selected_filters){
  let {mesh_elements_geojson, mesh_elements_ref, mesh_elements_leg} = objects

  let value = (e) => e["carburant_pourcentage"]
  let is_available = (e) => e["carburant_pourcentage"] !== null

  let choro_legend = {
    thresholds: [0, 9, 11, 13.8, 17, 20, 100],
    colors: c_gradient_reds_greens.slice(2, 8).reverse(),
    references: [
      {label: "France", value: formatFigure(13.8)},
    ],
    title: `Part des ménages en précarité énergétique mobilité`,
    unit: "%",
    format: (d) => formatFigure(d)
  }

  let choro_layer = new ChoroLayer({
    geojson: mesh_elements_geojson,
    getValue: (d) => value(d),
    getLabel: (d) => is_available(d) ? `<b>${formatFigure(value(d))}</b> %  des ménages en précarité énergétique mobilité` : "<i>donnée indisponible</i>",
    legend: choro_legend
  });

  return [choro_layer]
}


function getMeshElementsTable(objects, selected_filters){
  let headlines = [], cols = [], format_table = [], format_csv = [], align = [];
  let mesh_elements = objects.mesh_elements_geojson.features.map((f) => f.properties)

  let value = (e) => e["carburant_pourcentage"]

  headlines.push("Part des ménages en précarité énergétique mobilité")
  cols.push(mesh_elements.map((c)=> value(c)))
  format_table.push((f)=>formatFigure(f))
  format_csv.push((f)=>formatFigure(f))
  align.push("r")

  return {headlines, cols, format_table, format_csv, align}
}


export const precariousness_fuel = new Indicator({
    indicator: "precariousness_fuel",
    label: "précarité énergétique mobilité",
    data_source: "verified",
    description: "Les ménages en situation de précarité énergétique mobilité sont les ménages sous le 3ème décile de revenu, dont les dépenses énergétiques pour le carburant de la mobilité quotidienne sont supérieures à 4,5% des revenus.",

    tables: {
      mesh: getMeshElementsTable
    },
    layers : {
      choropleth: getChoroLayer
    },
    datasets_names: ["territory/precariousness"]
})
