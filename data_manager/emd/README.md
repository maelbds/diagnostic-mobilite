## Données des enquêtes locales (EMD, EDGT, EMC²)

Pour ajouter des données locales, plusieurs étapes sont nécessaires :

1. Créer un dossier `nom_enquete/` au nom de l'enquête.
2. Dans celui-ci, créer les dossiers `datasets/`, `doc/` et `geo/`
3. Dans `datasets/`, ajouter et renommer les fichiers de l'enquête : 
`persons.csv` (PERSONNES), `households.csv` (MENAGES), `travels.csv` (DEPLACEMENTS), `travels_parts.csv` (TRAJETS). 
   Si besoin, utiliser le fichier `dataset_txt_to_csv.py` pour transformer un fichier .txt en .csv.
4. Copier/coller dans votre dossier `nom_enquete/` les fichiers `dictionnary.csv`, `dictionnary_modes.csv`, 
   `dictionnary_reasons.csv` présents dans le dossier `montpellier/`. Modifier les trois .csv
   pour les adapter à la structure de votre enquête en utilisant le(s) fichier(s) Dico.
5. Exécuter alors le script `read_datasets_and_save_to_db.py`
   
Pour la partie géographique maintenant:

1. Dans `geo/`, ajouter les fichiers .geojson ou shp de définitions des zones fines, générateurs de trafic et zones externes.
2. Adapter le fichier `read_geo_and_save_to_db.py` pour enregistrer les zones géographiques selon le format et les champs dans la BDD


Voir les liens vers les documents méthodologiques dans `data_manager/` 
pour plus de détails sur le traitement des enquêtes locales.
