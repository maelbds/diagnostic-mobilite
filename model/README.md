## Modèle

### Description

Cette partie du projet permet de **générer les objets qui vont représenter notre territoire**, sur un mode POO. 
Puis de **générer l'objet json transmis à l'interface pour visualisation des données**.

#### -

L'objet `Territory` est à la base de celui-ci. Il sera lui même constitué des objets 
`Commune`, `Area`, `Place` et `PublicTransport`. 

Comme on l'a vu, dans le cas où aucune enquête locale de déplacement n'est 
disponible, une modélisation est effectuée ([voir documentation du modèle](https://mobam.fr/diagnostic-mobilite/docs/methodologie_modelisation_v1.pdf)).
Cette organisation en POO est surtout utile pour faciliter cette modélisation. 
Les dossiers `territorial_anchorage/`, `synthetic_population/` et `mobility_pattern/` 
sont utiles aux différentes étapes successives décrites dans la documentation du modèle.

#### -

L'objet `TerritoryOutput` est ensuite créé pour générer les informations qui constitueront l'objet json
envoyé en réponse à la requête de l'interface. Celle-ci affichera donc la page de visualisation du diagnostic à partir du json.

Ce dernier objet fait principalement appel aux fonctions présentes dans le dossier `data_analysis/` 
notamment pour opérer le traitement des données de pratiques de déplacement. 
Voir la [méthodologie de traitement des enquêtes déplacements](https://mobam.fr/diagnostic-mobilite/docs/methodologie_traitement_v1.pdf).



