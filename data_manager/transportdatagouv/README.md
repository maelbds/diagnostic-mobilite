## transport.data.gouv data

Dans ce dossier sont réunis les fichiers permettant de sauvegarder dans la base de données
 et d'y lire les données des :
 - infrastructures cyclables (cycle_paths)
 - stationnements vélo (cycle_parkings)
 - lieux de covoiturage (bnlc)
 - bornes de recharge électriques (irve)
 - périmètres ZFE (zfe)
 - transports en commun (à partir des fichiers GTFS)

**Pour les 5 premiers, le fonctionnement est similaire à la majorité des données traitées dans le projet** : 
on enregistre le fichier indiqué par `source.py` dans le dossier `data/` adéquat puis le fichier `save_XXX.py` 
permet de l'enregistrer dans la base de données. 

Pour les données de transport en commun, on utilise le fichier `update_pt_datasets.py`. 
Celui-ci va appeler l'API transport.data.gouv pour obtenir la liste des jeux de données de 
transports en commun disponibles puis enregistrer ceux qui ne sont pas déjà dans la base de données. 
Pour cela, le script télécharge le fichier ZIP associé au jeu de données, extrait l'archive puis traite le fichier GTFS 
avant de l'enregistrer dans la BDD. Celle-ci est organisée de la même manière que la structure du GTFS : agency, calendar, routes, stops, stop_times, trips. 
On y ajoute une table datasets et une table geo_codes qui permet d'associer des codes communes INSEE aux lignes de transport. 
De cette manière, il est beaucoup plus rapide d'obtenir les lignes de transport associées à une commune (cf `get_public_transport2()`, WORK IN PROGRESS).

**En résumé, il suffit donc d'exécuter `update_pt_datasets.py/update_pt_datasets()` pour remplir la base de données.**