import {pattern_dedicated_cycle_paths, pattern_shared_cycle_paths, pattern_cycle_parkings} from '../a-Graphic/Layout';

import {PathLayer} from '../i-Map/Layers/PathLayer';
import {PointLayer} from '../i-Map/Layers/PointLayer';

import {cols_to_rows, titleCase} from '../f-Utilities/util_func';

import {Indicator} from '../g-Components/Indicator';


let dedicated_ame = ["PISTE CYCLABLE", "DOUBLE SENS CYCLABLE PISTE", "VOIE VERTE", "VELO RUE", "COULOIR BUS+VELO"]
let shared_ame = ["BANDE CYCLABLE", "DOUBLE SENS CYCLABLE BANDE", "DOUBLE SENS CYCLABLE NON MATERIALISE",
                  "AMENAGEMENT MIXTE PIETON VELO HORS VOIE VERTE", "CHAUSSEE A VOIE CENTRALE BANALISEE"]

let filter_dedicated = (d) => dedicated_ame.includes(d.properties.ame_d) | dedicated_ame.includes(d.properties.ame_g)
let filter_shared = (d) => shared_ame.includes(d.properties.ame_d) | shared_ame.includes(d.properties.ame_g)

function name_ame(ame_g, ame_d){
  if (ame_g == "AUCUN"){
    return titleCase(ame_d)
  } else if (ame_d == "AUCUN"){
    return titleCase(ame_g)
  } else {
    return titleCase(ame_d) + " & " + titleCase(ame_g)
  }
}


function getCyclePathsShareLayer(objects, selected_filters){
  let {cycle_paths} = objects

  let pt_legend = {
    pattern: pattern_shared_cycle_paths,
    title: `Voie partagée`
  }

  let path_layer = new PathLayer({
    geojson: cycle_paths,
    filter: filter_shared,
    getLabel: (d) => `${name_ame(d.ame_g, d.ame_d)} <i>(mis à jour le ${(new Date(Date.parse(d.date_maj))).toLocaleDateString("fr-FR")})`,
    pattern: pattern_shared_cycle_paths,
    legend: pt_legend,
  });

  return [path_layer]
}

function getCyclePathsDedicatedLayer(objects, selected_filters){
  let {cycle_paths} = objects

  let pt_legend = {
    pattern: pattern_dedicated_cycle_paths,
    title: `Voie dédiée`
  }

  let path_layer = new PathLayer({
    geojson: cycle_paths,
    filter: filter_dedicated,
    getLabel: (d) => `${name_ame(d.ame_g, d.ame_d)} <i>(mis à jour le ${(new Date(Date.parse(d.date_maj))).toLocaleDateString("fr-FR")})`,
    pattern: pattern_dedicated_cycle_paths,
    legend: pt_legend,
  });

  return [path_layer]
}

function getCycleParkingsLayer(objects, selected_filters){
  let {cycle_parkings} = objects

  let pt_legend = {
    pattern: pattern_cycle_parkings,
    title: `Stationnement vélo`
  }

  let cycle_parkings_layer = new PointLayer({
    geojson: cycle_parkings,
    filter: (d) => true,
    getLabel: (d) => `${d.capacite === null ? "/" : d.capacite} places <i>(mis à jour le ${(new Date(Date.parse(d.date_maj))).toLocaleDateString("fr-FR")})`,
    pattern: pattern_cycle_parkings,
    legend: pt_legend,

  });

  return [cycle_parkings_layer]
}

function getCycleLayer(objects, selected_filters){
  let layers = []
  layers = layers.concat(getCyclePathsDedicatedLayer(objects, selected_filters))
  layers = layers.concat(getCyclePathsShareLayer(objects, selected_filters))
  layers = layers.concat(getCycleParkingsLayer(objects, selected_filters))
  return layers
}


export const cycle = new Indicator({
    indicator: "cycle",
    label: "infrastructures cyclables",

    filters: [],

    tables: {},
    layers : {
      path: getCycleLayer,
    },
    description: "Les voies dédiées concernent les pistes cyclables, voies vertes, vélo-rues et couloir bus+vélo. Les voies partagées concernent les bandes cyclables, double-sens cyclables, et chaussées à voie centrale banalysée.",


    datasets_names: ["offer/cycle_paths", "offer/cycle_parkings"]
  })
