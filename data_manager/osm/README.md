## osm data

On utilise les données OpenStreetMap simplement pour obtenir 
les voies de chemin de fer au niveau communal.

Ainsi, à chaque appel de la fonction `get_railways()`, on regarde dans la BDD si 
la donnée a déjà été enregistrée pour la commune, si oui on l'utilise, si non on
envoie une requête à l'API Overpass pour l'obtenir.

**Il n'y a donc pas de base de données globale a enregistrée ici, elle se remplira au fur et à mesure des appels à la fonction.**

_Ce fonctionnement a été mis en place au début du projet. Il a vocation à être remplacé
par la donnée IGN BD TOPO ainsi que les jeux de données du train fournis par transport.data.gouv._