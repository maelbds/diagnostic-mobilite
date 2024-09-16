# Diagnostic Mobilité

Le commun Diagnostic Mobilité a pour objectif d'**accompagner les territoires pour construire une mobilité durable**. 
Pour cela, il propose une application web qui rassemble des indicateurs pour **comprendre les enjeux de mobilité 
d’un territoire** préalablement sélectionné (en France, principalement à l'échelle d'un EPCI). 

Voir [l'interface en ligne](https://diagnostic-mobilite.fr/app).

![interface](https://diagnostic-mobilite.fr/images/outil/outil1l.jpg)

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
 - `interface/` contient les pages de sélection et visualisation de l'outil de diagnostic. 
   C'est l'interface à laquelle on accède à cette adresse [https://diagnostic-mobilite.fr/app](https://diagnostic-mobilite.fr/app).
   Elle permet d'envoyer une requête au back, et d'afficher la réponse obtenue.

et d'un back Python, organisé en trois parties :
 - ```data_manager/``` permet de collecter les données sources, de les traiter puis de créer et remplir les tables 
  correspondantes dans la base de données. On trouve donc des sous dossiers pour chacune des sources, 
  avec pour chacune d'elle le script de collecte, traitement et mise en base.
 - ```compute_model/``` permet le calcul des déplacements. Celui-ci s'effectue en deux grandes étapes :
    1. Tout d'abord, on crée une population synthétique pour chacune des communes qui composent les EPCIs étudiés. 
       C'est le rôle du dossier ```a_synthetic_population```.
    2. On calcule les déplacements en associant les individus de la population synthétique avec les individus 
       enquêtés de l'EMP. Cette fois, l'opération s'effectue à l'échelle de l'EPCI en renseignant les codes INSEE des 
       communes le composant. C'est le rôle du dossier ```b_survey_association```. Lors de cette opération, 
       il est nécessaire de caractériser le territoire étudié, les éléments requis sont ainsi renseignés dans
       le dossier ```t_territory```.
    3. Une fois les déplacements calculés, le dossier ```c_analysis``` contient une fonction qui calcule quelques 
       indicateurs à l'échelle du territoire d'étude ce qui permet de contrôler la cohérence des résultats obtenus.
    4. Enfin, ```d_export``` permet d'exporter les déplacements calculés et enregistrés dans la base de données dans des 
       fichiers csv par région.
       
    Le fichier ```main.py``` permet d'opérer tous les calculs et le fichier ```sources.py``` compile les sources de 
    données utilisées par le modèle. La documentation détaillée de la méthodologie [est disponible ici](https://diagnostic-mobilite.fr/docs/methodologie_modelisation_v1.pdf).
 - `api/` est naturellement l'api qui répond aux requêtes du front


## Installation

### Prérequis :

- Git
- Docker

A titre informatif, les calculs de la modélisation ont été effectués avec le matériel suivant :
- OS : Debian 12
- Mémoire : 8Go + swap memory
- Processeur : 8 CPU
- Stockage : 50Go requis environ


### Étapes :

#### Back

1. Importer le code depuis le répertoire git

    ```git clone https://github.com/maelbds/diagnostic-mobilite.git```


2. Modifier les droits pour permettre l'écriture lors du téléchargement des bases de données

    ```chmod -R 777 diagnostic-mobilite```


3. Se rendre dans le dossier du projet

    ```cd diagnostic-mobilite```


4. Créer la base de données

    ```docker network create diag_mob_app```

    ```docker volume create diag_mob_db```

    ```docker run --network diag_mob_app --network-alias mymariadb -v diag_mob_db:/var/lib/mysql --name mariadb_container --env MARIADB_DATABASE=diagnostic_mobilite --env MARIADB_ROOT_PASSWORD={PASSWORD} mariadb```


5. Créer l'application et l'environnement associés au répertoir (vérifier à bien être placé dans le dossier ```diagnostic-mobilite```).

    ```docker build -t diag-mob-app .```

    ```docker run --name app_container -it --env DB_PASSWORD={PASSWORD} --network diag_mob_app --mount type=bind,src="$(pwd)",target=/app diag-mob-app```

Le conteneur Docker créé (```app_container```) permet d'exécuter des instructions bash. Dans le conteneur on va donc successivement :


7. Pour finir l'installation, on remplit la base de données (le script télécharge les fichiers des sources de données 
requises, les traite, crée et remplit les tables). *Cette opération prend quelques heures (traitement de fichiers volumineux)*.

    ```python -m data_manager.load_db```

7. (Optionnel) Pour calculer les déplacements des territoires non couverts par une enquête mobilité locale avec le modèle. 
   On peut exécuter la commande suivante. Celle-ci se fait en deux étapes (calcul des populations synthétiques 
   puis calcul des déplacements) et prend quelques jours avec le matériel spécifié ci-dessus.

    ```python -m compute_model.main```

8. Enfin, pour lancer le serveur afin que l'API soit en écoute sur le port 8000, on effectue la commande : 

    ```gunicorn -w 2 -b 0.0.0.0:8000 --timeout 600 'api.app:app'```

A tout moment, on peut "sortir" du conteneur sans interrompre son exécution avec CTRL P+Q. On peut "entrer" dans le 
conteneur avec ```docker attach app_container```. Consulter le journal du conteneur avec ```docker logs app_container```.

A ce stade, le back est prêt. Il reste à configurer le front.

#### Front


- Avec l'invite de commande (cmd) :
  - Se rendre dans le dossier du projet : `cd votre_chemin/diagnostic-mobilite`
  - Créer le projet react avec npm : `npx create-react-app interface`
- Un dossier `interface/` est créé dans votre dossier `diagnostic-mobilite/`. Il contient tous les éléments du projet React.
- Dans ce dossier interface, **supprimer les dossiers `public/` et `src/`, ainsi que le fichier** `package.json` qui contient les librairies à installer. **Remplacez-les** par ceux du répertoire Git.
- De retour dans l'invite de commande, rendez-vous dans le dossier de l'interface `cd interface` puis installez les librairies `npm install`. 
- Vous pouvez alors démarrer l'interface : `npm start`.



## Contribution

Ce projet est un commun et tout retour est le bienvenue 
pour contribuer à l'amélioration du modèle!



