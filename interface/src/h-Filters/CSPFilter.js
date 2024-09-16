import {Filter} from './Filter';


export const CSPFilter = new Filter({
  name: "pop_csp",
  init:  ["4", "5"],
  title: "catégories socio-professionnelles",
  labels: {
            "1": "Agriculteurs·rices exploitant·es",
            "2": "Artisan·es, commerçant·es, chef·fes d'entreprise",
            "3": "Cadres et professions intellectuelles supérieures",
            "4": "Professions intermédiaires",
            "5": "Employé·es",
            "6": "Ouvrier·es",
            "7": "Retraité·es",
            "8": "Autre sans activité professionnelle",
          }
,
  legend: {
            "1": "Agriculteurs·rices",
            "2": "Artisan·es, commerçant·es, chef·fes d'entreprise",
            "3": "Cadres",
            "4": "Prof. intermédiaires",
            "5": "Employé·es",
            "6": "Ouvrier·es",
            "7": "Retraité·es",
            "8": "Autre",
          }
})
