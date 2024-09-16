import {pattern_irve} from '../a-Graphic/Layout';

import {PointLayer} from '../i-Map/Layers/PointLayer';

import {cols_to_rows, titleCase} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';



function getIRVELayer(objects, selected_filters){
  let {irve} = objects

  let pt_legend = {
    pattern: pattern_irve,
    title: `Borne de recharge électrique`
  }

  let irve_layer = new PointLayer({
    geojson: irve,
    filter: (d) => true,
    getLabel: (d) => `<b>${d.nom_station === null ? "" : d.nom_station}</b> ${d.nbre_pdc === null ? "/" : d.nbre_pdc} point(s) de charge - ${d.puissance_nominale === null ? "/" : d.puissance_nominale}kW <i>(mis à jour le ${(new Date(Date.parse(d.date_maj))).toLocaleDateString("fr-FR")})`,
    pattern: pattern_irve,
    legend: pt_legend,

  });

  return [irve_layer]
}



export const irve = new Indicator({
    indicator: "irve",
    label: "bornes de recharge électrique",

    filters: [],

    tables: {},
    layers : {
      path: getIRVELayer,
    },

    datasets_names: ["offer/irve"]
  })
