import {Filter} from './Filter';


export const GenderFilter = new Filter({
  name: "gender",
  init: "all",
  labels: {
    "all": "Ensemble",
    "m": "Hommes",
    "f": "Femmes"
  },
  legend: {
    "all": "hab",
    "m": "hommes",
    "f": "femmes"
  }
})
