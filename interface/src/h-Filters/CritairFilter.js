import {Filter} from './Filter';


export const CritairFilter = new Filter({
  name: "critair_filter",
  init:  ["elec", "critair1", "critair2"],
  labels: {
            "elec": "Crit'Air E",
            "critair1": "Crit'Air 1",
            "critair2": "Crit'Air 2",
            "critair3": "Crit'Air 3",
            "critair4": "Crit'Air 4",
            "critair5": "Crit'Air 5",
            "nc": "Non classé",
          }
,
  legend: {
            "elec": "Crit'Air électrique",
            "critair1": "Crit'Air 1",
            "critair2": "Crit'Air 2",
            "critair3": "Crit'Air 3",
            "critair4": "Crit'Air 4",
            "critair5": "Crit'Air 5",
            "nc": "non classés",
          }
})
