# Diagnostic Mobilité - Interface

## Organisation

Cette interface, sous la forme d'une application web React, a deux objectifs :
1. **Sélectionner le territoire d'études** et ces zones. Cela se fait avec la page de sélection `0-Home/Selection.js`, elle même découpée en trois sous-étapes :
   1. Sélection des communes d'intérêt `5-Selection/SelectionMap.js`
   2. Sélection des zones `5-Selection/SelectedMap.js`
   2. Récapitulatif de la sélection `5-Selection/SelectedTerritory.js` et validation du territoire d'étude pour envoi d'une requête au serveur. 
      
2. **Visualiser le diagnostic obtenu**. Ce dernier se présente sous la forme d'un fichier json, directement reçu depuis le serveur, ou stocké dans le dossier `public/`. 
   La page `0-Home/Diagnostic.js` charge le fichier json et affiche les sections du diagnostic :
   1. En haut de page les **chiffres clés** `1-KeyFigures`
   2. Puis trois sections clickables :
   3. **Description du territoire** `2-TerritoryProfile/`
   3. **Offre de transport** `3-MobilityOffer/`
   3. **Pratiques de déplacement** `4-MobilityProfile/`
    
Ensuite, chacune des sections est découpée en plusieurs composants selon la logique de React.

## Technologies

La mise en page utilise BootStrap v4. Les compléments css sont dans le fichier `index.css`.

Les cartes de la page sélection sont des canvas générés avec d3.js ([cf notebook d'Eric Mauvière](https://observablehq.com/@ericmauviere/typologie-communale?collection=@ericmauviere/france-par-communes-2021)). 

Les cartes de la page visualisation sont générées avec Leaflet. Un élément carte est généré depuis le fichier `b-LeafletMap/leaflet_map.js`, 
puis on ajoute les couches d'informations depuis les éléments souhaités dans `b-LeafletMap/LeafletMapElement/`.

Les graphiques sont générés avec Plotly.js. Là encore on retrouve les formats utilisés dans `c-PlotlyFigures/`.


## Paramètres généraux

Depuis le fichier racine App.js, les paramètres d'état permettent :
- `manual_mode` Si true, choisir d'afficher la page de visualisation du diagnostic enregistré dans le fichier json indiqué par `file_if_manual_mode`. Si false, afficher la page de sélection, pour une utilisation avec le serveur.
- `graphic_chart` Si true, affiche la charte graphique en bas de page de visualisation
- `dev_mode` Si true, affiche une quatrième section DEV, utile pour développer de nouveaux indicateurs.


