## Server

### Description

Le script `server.py` permet de générer un serveur Flask. 
Il écoute les requêtes envoyées par l'interface pour générer un objet `Territory`
puis `TerritoryOutput`. Ce dernier est renvoyé à l'interface sous la forme d'un json. 
Le json est également stocké localement ce qui permet une utilisation manuelle avec 
l'interface par la suite (cf documentation correspondante).

**En résumé, `server.py` établit la connexion entre l'interface et le modèle.**



