import {pattern_bnlc} from '../a-Graphic/Layout';

import {PointLayer} from '../i-Map/Layers/PointLayer';

import {cols_to_rows, titleCase} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';



function getBNLCLayer(objects, selected_filters){
  let {bnlc} = objects

  let pt_legend = {
    pattern: pattern_bnlc,
    title: `Lieu de covoiturage`
  }

  let bnlc_layer = new PointLayer({
    geojson: bnlc,
    filter: (d) => true,
    getLabel: (d) => `<b>${d.name === null ? "" : d.name}</b> ${d.nbre_pl === null ? "/" : d.nbre_pl} places de parking dont ${d.nbre_pmr === null ? "/" : d.nbre_pmr} PMR <i>(mis à jour le ${(new Date(Date.parse(d.date_maj))).toLocaleDateString("fr-FR")})`,
    pattern: pattern_bnlc,
    legend: pt_legend,

  });

  return [bnlc_layer]
}



export const bnlc = new Indicator({
    indicator: "bnlc",
    label: "lieux de covoiturage",

    filters: [],

    tables: {},
    layers : {
      path: getBNLCLayer,
    },

    datasets_names: ["offer/bnlc"]
  })
