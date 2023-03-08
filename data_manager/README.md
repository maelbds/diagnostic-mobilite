## Data Manager

### Description

L'objectif de cette partie du projet est d'organiser et stocker toutes les données utilisées. 
Elles sont séparées dans des dossiers par fournisseur de la source de données.
Le fichier `main.py` centralise l'ensemble des sources de données, qui seront utilisées dans l'interface.
Il rassemble aussi quelques fonctions pour obtenir des données.


### Installation

Les données ne sont pas enregistrées sur le répertoire Git. Il est donc nécessaire
de les télécharger puis de les enregistrer dans la BDD. Pour cela :
1. Chaque dossier comporte un fichier `source.py` avec les liens vers les fichiers à télécharger.
2. Placer le(s) fichier(s) téléchargé(s) dans le dossier `data/`
3. Exécuter le(s) fichier(s) `save_to_db_XXXX.py` en adaptant le chemin si besoin.

Certaines données ont un fonctionnement différent et l'installation est décrite dans le dossier correspondant.
C'est le cas pour :
- emd
- osm
- transportdatagouv/public_transport

_Ce processus est long et répétitif. Un script pour l'automatiser sera proposé._


### Documentation

En complément, sont disponibles : 

- [La méthodologie de traitement des enquêtes déplacements](https://mobam.fr/diagnostic-mobilite/docs/methodologie_traitement_v1.pdf)
- [La méthodologie de modélisation](https://mobam.fr/diagnostic-mobilite/docs/methodologie_modelisation_v1.pdf) qui présente notamment le traitement de l'EMP
