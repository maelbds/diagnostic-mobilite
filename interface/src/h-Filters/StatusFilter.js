import {Filter} from './Filter';


export const StatusFilter = new Filter({
  name: "pop_status",
  init:  ["employed"],
  labels: {
            "employed": "actifs & actives",
            "unemployed": "au chômage",
            "retired": "à la retraite",
            "scholars_m17": "scolaires (jusqu'à 17 ans)",
            "scholars_18": "scolaires (18 ans et plus)",
            "other": "autres",
          }
,
  legend: {
            "employed": "actifs & actives",
            "unemployed": "au chômage",
            "retired": "à la retraite",
            "scholars_m17": "scolaires (jusqu'à 17 ans)",
            "scholars_18": "scolaires (18 ans et plus)",
            "other": "autres",
          }
})
