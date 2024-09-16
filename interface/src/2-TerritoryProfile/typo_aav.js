export const typo_zaav = [
   {"code":"11","libelle":"Pôle AAV < 50 000 hab","couleur":"#F6B7C2"},
   {"code":"12","libelle":"Pôle AAV 50 000 ↔ 200 000 hab","couleur":"#F15D7D"},
   {"code":"13","libelle":"Pôle AAV 200 000 ↔ 700 000 hab","couleur":"#E40038"},
   {"code":"14","libelle":"Pôle AAV > 700 000 hab","couleur":"#A91535"},
   {"code":"15","libelle":"Pôle AAV > 700 000 hab","couleur":"#A91535"},
   {"code":"21","libelle":"Couronne AAV < 50 000 hab","couleur":"#F5F0AF"},
   {"code":"22","libelle":"Couronne AAV 50 000 ↔ 200 000 hab","couleur":"#EDE049"},
   {"code":"23","libelle":"Couronne AAV 200 000 ↔ 700 000 hab","couleur":"#FFB520"},
   {"code":"24","libelle":"Couronne AAV > 700 000 hab","couleur":"#EE9008"},
   {"code":"25","libelle":"Couronne AAV > 700 000 hab","couleur":"#EE9008"},
   {"code":"30","libelle":"","couleur":"#DAD8D2"} // avant : #F3F2F0
 ]
 export const typo_zaav_legend = [
    {"code":"11","cat":"Pôle", "type": "AAV <50k hab","couleur":"#F6B7C2"},
    {"code":"12","cat":"Pôle", "type": "AAV 50k-200k hab","couleur":"#F15D7D"},
    {"code":"13","cat":"Pôle", "type": "AAV 200k-700k hab","couleur":"#E40038"},
    {"code":"14","cat":"Pôle", "type": "AAV >700k hab","couleur":"#A91535"},
    {"code":"21","cat":"Couronne", "type": "AAV - 50k hab","couleur":"#F5F0AF"},
    {"code":"22","cat":"Couronne", "type": "AAV 50k - 200k hab","couleur":"#EDE049"},
    {"code":"23","cat":"Couronne", "type": "AAV 200k - 700k hab","couleur":"#FFB520"},
    {"code":"24","cat":"Couronne", "type": "AAV + 700k hab","couleur":"#EE9008"},
    {"code":"30","cat":"Hors attraction des villes", "type": "","couleur":"#DAD8D2"}
  ]
export const typo_map_color = new Map( typo_zaav.map(d => [d.code, d.couleur]))
export const typo_map_name = new Map( typo_zaav.map(d => [d.code, d.libelle]))
