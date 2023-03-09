# Diagnostic Mobilité

Le commun Diagnostic Mobilité a pour objectif d'**accompagner les territoires pour construire une mobilité durable**. 
Pour cela, il propose une application web qui rassemble des indicateurs pour **comprendre les enjeux de mobilité 
d’un territoire** préalablement sélectionné (en France métropolitaine, principalement à l'échelle d'un EPCI). 

Voir les pages de démonstration : [interface de sélection du territoire](https://mobam.fr/diagnostic-mobilite/selection/), 
puis [interface de visualisation du diagnostic](https://mobam.fr/diagnostic-mobilite/visualisation/).


![interface de sélection](https://mobam.fr/images/overview_selection.png)
![interface de visualisation](https://mobam.fr/images/overview_visualisation.png)

_Ce projet est réalisé avec le soutien financier de l'ADEME 
dans le cadre de [l'appel à communs résilience des territoires](https://wiki.resilience-territoire.ademe.fr/wiki/Diagnostic_Mobilit%C3%A9)._


## Fonctionnement

Cet outil rassemble, traite et met en page plusieurs sources de données pour établir un 
état des lieux complet des enjeux de mobilité d'un territoire, organisé en trois sections :
 - description du territoire
 - offre de transport
 - pratiques de déplacement

On retrouve principalement des données de l'INSEE pour renseigner la première section et des données du PAN,
transport.data.gouv, pour établir la deuxième section. Quant à la section pratiques de déplacement, deux cas de
figure se distinguent :
 - si une enquête locale des déplacements est disponible sur le territoire d'étude (EMD, EDGT ou EMC²), c'est elle qui sera analysée.
   (voir la [méthodologie de traitement des enquêtes déplacements](https://mobam.fr/diagnostic-mobilite/docs/methodologie_traitement_v1.pdf))
 - sinon, une modélisation permet d'obtenir une estimation des pratiques de déplacement.
   [La méthodologie de modélisation est présentée ici.](https://mobam.fr/diagnostic-mobilite/docs/methodologie_modelisation_v1.pdf) 
   Elle est particulièrement adaptée pour les territoires en milieu peu dense, non couverts par les enquêtes locales.


## Structure

L'ensemble du code de cette application web est rassemblé dans ce répertoire. 
Celle-ci est constituée d'une interface React :
 - `interface/` regroupe les pages de sélection et visualisation présentées plus haut.
   Elle permet d'envoyer une requête au back, et d'afficher la réponse obtenue.

et d'un back Python, organisé en trois parties :
 - `data_manager/` organise et gère les différentes sources de données, en lien avec la BDD
 - `model/` constitue l'objet territoire étudié, opère la modélisation et le traitement des données
 - `server/` crée un server qui traite les requêtes envoyées par l'interface et y répond

## Installation

### Prérequis :

- Python 3.7
- Un environnement de développement Python (ex: PyCharm) 
- Node.js (npm) (https://nodejs.org/en/)
- Un dossier qui constitue l'emplacement du projet, on le nommera ici `diagnostic-mobilite/` 

### 1 - Mise en place de l'interface React :

- Avec l'invite de commande (cmd) :
  - Se rendre dans le dossier du projet : `cd votre_chemin/diagnostic-mobilite`
  - Créer le projet react avec npm : `npx create-react-app interface`
- Un dossier `interface/` est créé dans votre dossier `diagnostic-mobilite/`. Il contient tous les éléments du projet React.
- Dans ce dossier interface, **supprimer les dossiers `public/` et `src/`, ainsi que le fichier** `package.json` qui contient les librairies à installer. **Remplacez-les** par ceux du répertoire Git.
- De retour dans l'invite de commande, rendez-vous dans le dossier de l'interface `cd interface` puis installez les librairies `npm install`. 
- Vous pouvez alors démarrer l'interface : `npm start`.


### 2 - Mise en place du back Python

- Au sein de votre environnement de développement Python, dans le dossier `diagnostic-mobilite/` créez un environnement virtuel (venv) qui exécute Python3.7.
- Dans le même dossier, importer les dossiers `data_manager/`, `model/`, `server/` ainsi que le fichier `requirements.txt` depuis le répertoire Git 
- Installer les packages du projet (vous pouvez utiliser la commande `pip install -r requirements.txt`)


### 3 - Mise en place de la base de données

- Installer MariaDB en suivant les instructions de la page https://www.mariadbtutorial.com/getting-started/install-mariadb/. 
  (Ou autre système de BDD, en prenant soin de modifier le fichier `data_manager/database_connection/sql_connect.py` en conséquence.)
- Si vous avez choisi MariaDB, vous pouvez utiliser HeidiSQL qui est le gestionnaire de BDD associé. 
  Il permet facilement de créer des tables, d'y accéder, de les modifier.
- Dans `data_manager/database_structure/` se trouvent deux fichiers : `db_structure.pql` et `db_dictionnaries.sql`.
  Executer ces fichiers dans votre BDD pour créer les tables. 
- Connecter le projet Python à la BDD : dans `data_manager/database_connection/`, créer un fichier `db_connection_info.py` et renseigner les variables selon le modèle `db_connection_info_example.py`.
- Remplir la BDD selon les indications présentes dans `data_manager/`


### 4 - Utilisation

- Démarrer le serveur Flask en exécutant le fichier `server/server.py`
- Démarrer l'interface React :
  - Ouvrir l'invite de commandes (cmd)
  - Se rendre dans le dossier de l'interface `cd votre_chemin/diagnostic-mobilite/interface/`
  - Puis `npm start`
- L'interface s'ouvre dans votre navigateur : Diagnostic Mobilité est fonctionnel.

