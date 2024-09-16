import {Filter} from './Filter';


export const NbDistFilter = new Filter({
  name: "nb_dist_filter",
  init: "distance",
  title: "compter les déplacements en",
  labels: {
    "distance": "distance",
    "number": "nombre",
  },
  legend: {
    "distance": "km",
    "number": "déplacements",
  }
})
