import {Filter} from './Filter';


export const PTModesFilter = new Filter({
  name: "modes",
  init:  ["train", "bus"],
  labels: {
            "train": "Train",
            "metro": "Métro",
            "tram": "Tramway",
            "bus": "Bus",
            "other": "Autre",
          }
,
  legend: {
            "train": "Train",
            "metro": "Métro",
            "tram": "Tramway",
            "bus": "Bus",
            "other": "Autre",
          }
})
