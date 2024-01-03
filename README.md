## Diagnostic Mobilité -  *Modélisation et calcul de déplacements*

### Présentation

Le commun Diagnostic Mobilité a pour objectif d'**accompagner les territoires pour construire une mobilité durable**. 
Pour cela, il propose une application web qui rassemble des indicateurs pour **comprendre les enjeux de mobilité d’un 
territoire** préalablement sélectionné (en France métropolitaine, principalement à l'échelle d'un EPCI).

Une partie importante du diagnostic réside dans la modélisation et le calcul des pratiques de déplacement dont une 
analyse est ensuite proposée. **Dans ce répertoire, on trouve le code qui permet de collecter les sources qui alimenteront
le modèle et l'algorithme qui permet le calcul des déplacements**.


### Prérequis :

Les calculs ont été effectués avec le matériel suivant :
- OS : Debian 12
- Mémoire : 8Go + swap memory
- Processeur : 8 CPU
- Stockage : 50Go requis environ

Les logiciels suivants doivent être installés au préalable :
- Docker
- Git


### Installation :

1. Importer le code depuis le répertoire git

    ```git clone https://github.com/maelbds/diagnostic-mobilite.git --branch terristory-tims```


2. Modifier les droits pour permettre l'écriture lors du téléchargement des bases de données

    ```chmod -R 777 diagnostic-mobilite```


3. Se rendre dans le dossier du projet

    ```cd diagnostic-mobilite```


4. Créer la base de données

    ```docker network create diag_mob_app```

    ```docker volume create diag_mob_db```

    ```docker run --network diag_mob_app --network-alias mymariadb -v diag_mob_db:/var/lib/mysql --name mariadb_container --env MARIADB_DATABASE=diagnostic_mobilite --env MARIADB_ROOT_PASSWORD={PASSWORD} mariadb```


5. Créer l'application et l'environnement associés au répertoire (vérifier à bien être placé dans le dossier ```diagnostic-mobilite```) 

    ```docker build -t diag-mob-app .```

    ```docker run --name app_container -it --env DB_PASSWORD={PASSWORD} --network diag_mob_app --mount type=bind,src="$(pwd)",target=/app diag-mob-app```

Le conteneur Docker créé (```app_container```) permet d'exécuter des instructions bash.


6. Pour finir l'installation, on remplit la base de données (le script télécharge les fichiers des sources de données 
requises, les traite, crée et remplit les tables). *Cette opération prend quelques heures (traitement de fichiers volumineux)*.

    ```python -m data_manager.load_db_compute_model```

A tout moment, on peut "sortir" du conteneur sans interrompre son exécution avec CTRL P+Q. On peut "entrer" dans le 
conteneur avec ```docker attach app_container```. Consulter le journal du conteneur avec ```docker logs app_container```.


### Utilisation

Le calcul s'effectue depuis le fichier ```compute_model.main```. 
En le modifiant on peut sélectionner la liste des EPCIs et EPTs dont on souhaite obtenir les déplacements. (Il est 
conseillé de produire les déplacements à l'échelle d'un EPCI ou EPT). 
Cela s'effectue dans la fonction ```get_territories```.

Le fichier en l'état permet de calculer les déplacements des territoires concernés par le programme TIMS au 
format requis par AURA EE qui exploitera les données par la suite pour calculer les empreintes énergetique 
et carbone des déplacements.

On effectue donc les calculs (qui seront stockés dans la base de données) avec la commande suivante 
dans le conteneur ```app_container``` :

```python -m compute_model.main```

On peut ensuite exporter les résultats (un fichier csv par région stockés dans 
```compute_model.d_export.data```) avec :

```python -m compute_model.d_export.export```

La liste des sources qui alimentent le modèle est disponible avec :

```python -m compute_model.sources```

### Organisation du code

Le code est scindé en deux grandes parties :

- ```data_manager``` permet de collecter les données sources, de les traiter puis de créer et remplir les tables 
  correspondantes dans la base de données. On trouve donc des sous dossiers pour chacune des sources, 
  avec pour chacune d'elle le script de collecte, traitement et mise en base.
- ```compute_model``` permet le calcul des déplacements. Celui-ci s'effectue en deux grandes étapes :
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


### Notice de traitement des déplacements calculés

#### Les variables

- ***id_ind*** - identifiant unique de la personne effectuant le déplacement - *str*
- ***id_trav*** - identifiant unique du déplacement - *str*
- ***trav_nb*** - numéro du déplacement dans la chaine de déplacements effectués par l'individu *id_ind* - *int*
- ***w_trav*** - coefficient de pondération du déplacement - *float*
- ***geo_code*** - code INSEE (COG 2021) de la commune de résidence de la personne effectuant le déplacement - *str*
- ***mode*** - code EMP du mode de déplacement principal du déplacement *cf modalités EMP* - *str*
- ***reason_ori*** - code EMP du motif d'origine du déplacement (cf modalités EMP) - *str*
- ***reason_des*** - code EMP du motif de destination du déplacement (cf modalités EMP) - *str*
- ***distance*** - distance du déplacement en km - *float*
- ***geo_code_ori*** - code INSEE (COG 2021) de la commune d'origine du déplacement - *str*
- ***geo_code_des*** - code INSEE (COG 2021) de la commune de destination du déplacement - *str*
- ***source_id*** - identifiant de l'individu enquêté de l'EMP, associé pendant la deuxième étape du modèle, cet identifiant correspond à la variable IDENT_IND dans les tables de l'EMP - *str*
- ***distance_emp*** - distance originale (en km) du déplacement de l'EMP associé pendant la deuxième étape du modèle, 
  non ajustée lors de la troisième étape de l'affectation des origines/destinations - *float*

#### Traitement des données

Chaque déplacement de la liste représente au global *w_trav* déplacements. 
Lors de l'analyse des déplacements, il convient donc de pondérer les attributs quantitatifs par *w_trav*.

Par exemple, pour calculer la distance totale d'un ensemble de déplacements, on multiplie pour chaque déplacement 
la distance du déplacement par le coefficient de pondération, puis on somme les distances ainsi pondérées. 
Le nombre total de déplacements correspond lui à la somme des coefficients de pondération.

Chaque individu *id_ind* correspond bien à un seul individu, on pourrait donc attribuer une colonne *w_ind* = 1.
Ainsi pour avoir la distance moyenne par personne, on calcule la distance totale parcourue puis on divise par le nombre 
d'individus uniques.


#### Indications pour le lien avec l'EMP

La méthodologie employée pour construire la demande de déplacements qui constitue le fichier des déplacements fonctionne
en trois temps ([détails ici](https://diagnostic-mobilite.fr/docs/methodologie_modelisation_v1.pdf)) :

1. Construction d'une population synthétique = clone fictif de la population du territoire d'étude
2. Association de chaque individu de la population synthétique avec un individu de l'EMP et avec lui ses déplacements
3. Attribution d'un lieu d'origine et de destination à chaque déplacement

Lors de l'étape 2, on enregistre l'identifiant de l'individu de l'EMP associé, c'est l'attribut *source_id* qui équivaut 
à *IDENT_IND* pour l'EMP. Chaque déplacement a aussi un attribut *trav_nb* directement repris depuis l'EMP. 
Le couple *source_id*=*IDENT_IND* & *trav_nb* est une clé qui permet d'identifier le déplacement original de l'EMP, et 
donc d'obtenir des variables de l'EMP non reprises dans les déplacements produits ici. 

Par exemple, le SDES qui produit l'EMP a récemment ajouté des informations sur les émissions de GES pour chaque déplacement
qui pourraient être utiles pour affiner le calcul des émissions (à approfondir selon la méthodologie du SDES, non disponible en ligne).


#### Exemple de résultats obtenus 

On donne ici des analyses obtenues selon les regroupements proposés dans le fichier ```correspondances_modes.csv```, données 
à titre d'exemple et de comparaison. 

- *Pour l'EPCI 200035848* :

```
-- MODES --
                     nombre - %  distance - %  effectif
mode_name_fr
autre                       0.9           0.9        66
moto                        0.5           0.9        28
transport en commun         3.1           3.9       235
voiture                    62.1          71.9      2635
voiture passager           13.1          17.4       894
vélo                        2.6           1.3       129
à pied                     17.6           3.7       940

-- DISTANCE --
Distance moyenne (km/pers) 36
```

- Pour l'EPCI *200035707* :

```
-- MODES --
                     nombre - %  distance - %  effectif
mode_name_fr
autre                       0.9           0.8       161
moto                        0.8           1.3        98
transport en commun         4.2           5.6       842
voiture                    62.5          72.6      7123
voiture passager           14.5          16.2      2560
vélo                        2.3           1.0       306
à pied                     14.7           2.6      2251

-- DISTANCE --
Distance moyenne (km/pers) 42
```

### Contribution

Ce projet est un commun et tout retour est le bienvenue 
pour contribuer à l'amélioration du modèle!

