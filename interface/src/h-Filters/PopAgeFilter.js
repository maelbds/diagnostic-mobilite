import {Filter} from './Filter';


export const PopAgeFilter = new Filter({
  name: "pop_age",
  init:  ["1529"],
  title: "classes d'âge",
  labels: {
              "14": "-14 ans",
              "1529": "15-29 ans",
              "3044": "30-44 ans",
              "4559": "45-59 ans",
              "6074": "60-74 ans",
              "7589": "75-89 ans",
              "90P": "+90 ans",
            }
,
  legend: {
              "14": "-14 ans",
              "1529": "15-29 ans",
              "3044": "30-44 ans",
              "4559": "45-59 ans",
              "6074": "60-74 ans",
              "7589": "75-89 ans",
              "90P": "+90 ans",
            }
})
