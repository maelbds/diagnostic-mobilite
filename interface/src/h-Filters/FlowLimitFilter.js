import {Filter} from './Filter';


export const FlowLimitFilter = new Filter({
  name: "flow_limit_filter",
  init: "25",
  title: "nombre de flux principaux à afficher",
  labels: {
    "25": "25",
    "50": "50",
    "100": "100",
    "200": "200",
    "all": "Tous",
  },
  legend: {
    "25": "25",
    "50": "50",
    "100": "100",
    "200": "200",
    "all": "Tous",
  },
})
