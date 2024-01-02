# Outil de Diagnostic Mobilité


## Installation

**1 - Prérequis :**

- Avoir Python 3.7
- Avoir un environnement de développement Python (ex: PyCharm) 
- Avoir Node.js (npm) (https://nodejs.org/en/)
- Télécharger MariaDB (instructions d'installation étape 4) (https://www.mariadbtutorial.com/getting-started/install-mariadb/)

**2 - Créer le projet React utilisé pour l'interface :**

- Créer un dossier qui contiendra tout le code du projet, on l'appelle *0.6Planet* 
- Avec l'invite de commande :
  - Se rendre dans le dossier créé : `cd votre_chemin/0.6Planet`
  - Créer le projet react avec npm : `npx create-react-app interface`
- Un dossier *interface* est créé dans votre dossier 0.6Planet, il contient tous les éléments du projet React
- Dans ce dossier interface, **supprimer les dossiers public et src**, ils seront remplacés par ceux du dépôt Git


**3 - Importer les fichiers depuis GitHub**

- Créer un projet dans votre environnement de développement Python, à la racine de votre dossier *0.6Planet*
- Créer un environnement virtuel associé (venv) qui utilise Python3.7, il permettra d'exécuter le code
- Cloner tous les fichiers contenus dans le répertoire GitHub (https://github.com/maelbds/0.6Planet.git), à la racine de votre projet
- Installer les packages du projet (vous pouvez utiliser la commande `pip install -r requirements.txt` dans le terminal de commande)

**4 - Créer la base de données**

- Installer MariaDB en suivant les instructions de la page https://www.mariadbtutorial.com/getting-started/install-mariadb/
  - Au cours de l'installation, garder `root` comme `user`, vous définirez un `password`, notez-le bien.
  - Laissez `port = 3306` et les autres paramètres par défaut
- Une fois MariaDB installé, votre serveur de BDD est prêt et HeidiSQL est également disponible : c'est le gestionnaire de BDD qui vous permettra de créer des tables, d'y accéder, de les modifier.
- Lancer HeidiSQL, rentrer les paramètres définis lors de l'installation, ouvrez la session et vous accédez à l'interface du gestionnaire
- Cliquer sur Fichier>Executer un fichier SQL : ouvrez le fichier db_structure.sql dans data_manager/db_backup/
- Cliquer sur l'icone rond vert "Rafraichir" : la base de données apparaît dans la colonne à gauche, elle contient les tables nécessaires au fonctionnement de l'outil

- Il faut maintenant connecter la base dans notre projet Python :
- Dans data_manager/database_connection/, créer un fichier db_connection_info.py et renseigner les variables suivantes :
  - `user = "root"`
  - `password = "votre_mdp"`
  - `host = "127.0.0.1"`
  - `port = 3306`
  - `database = "mobility_raw_data"`


**5 - Remplir la base de données**

Certaines tables sont des dictionnaires, on les remplit directement avec un fichier SQL :
- Cliquer sur Fichier>Executer un fichier SQL : ouvrez le fichier db_tables_with_data.sql dans data_manager/db_backup/
- Cliquer sur l'icone rond vert "Rafraichir" :  certaines tables comme reasons, types ou modes sont désormais remplies

D'autres tables, plus lourdes, doivent être remplies à partir de fichiers CSV à télécharger :
- ENTD :
  - Télécharger https://www.statistiques.developpement-durable.gouv.fr/sites/default/files/2021-12/donnees_individuelles_anonymisees_emp2019.zip
  - Placer les fichiers tcm_men_public.csv, q_menage_public.csv, tcm_ind_kish_public.csv, k_individu_public.csv, k_deploc_public.csv dans data_manager/entd/data/2018/
  - Dans save_data_from_csv_to_db_entd_2018.py, indiquer le bon chemin PATH
  - Changer `security = True` en `security = False`, puis exécuter UNE SEULE FOIS save_data_from_csv_to_db_entd_2018.py (PREND DU TEMPS)
  - Une fois le code executé, les tables entd dans la BDD sont remplies, remettre `security = True`

- INSEE BPE :
  - Télécharger https://www.insee.fr/fr/statistiques/fichier/3568638/bpe20_ensemble_xy_csv.zip
  - Placer le fichier bpe20_ensemble_xy.csv dans data_manager/insee_bpe/data/2020/
  - Dans save_data_from_csv_to_db_bpe.py changer `security = True` en `security = False`, puis exécuter UNE SEULE FOIS save_data_from_csv_to_db_bpe.py
  - Une fois le code executé, la table insee_bpe dans la BDD est remplie, remettre `security = True`

- INSEE CENSUS :
  - Télécharger https://www.insee.fr/fr/statistiques/fichier/5542859/RP2018_INDCVI_csv.zip (500Mo)
  - Placer le fichier FD_INDCVI_2018.csv dans data_manager/insee_census/data/2018/
  - Dans save_data_from_csv_to_db_census.py, indiquer le bon chemin PATH
  - Changer `security = True` en `security = False`, puis exécuter UNE SEULE FOIS save_data_from_csv_to_db_census.py (PREND DU TEMPS)
  - Une fois le code executé, la table insee_census_2018 dans la BDD est remplie, remettre `security = True`
  
- INSEE GENERAL :
  - DANS L'ORDRE
  - Dans save_data_from_csv_to_db_geocodes.py changer `security = True` en `security = False`, puis l'exécuter UNE SEULE FOIS, remettre `security = True`
  - Dans save_data_from_csv_to_db_canton.py changer `security = True` en `security = False`, puis l'exécuter UNE SEULE FOIS, remettre `security = True`
  - Dans save_data_from_csv_to_db_epci.py changer `security = True` en `security = False`, puis l'exécuter UNE SEULE FOIS, remettre `security = True`
  - Les tables insee_communes et insee_epci sont remplies

- INSEE MOBPRO :
  - Télécharger https://www.insee.fr/fr/statistiques/fichier/5395749/RP2018_mobpro_csv.zip (87Mo)
  - Placer le fichier FD_MOBPRO_2018.csv dans data_manager/insee_mobpro/data/2018/
  - Dans save_data_from_csv_to_db_mobpro.py, changer `security = True` en `security = False`, puis exécuter UNE SEULE FOIS save_data_from_csv_to_db_mobpro.py (PREND UN PEU DE TEMPS)
  - Une fois le code executé, la table insee_flows_home_work dans la BDD est remplie, remettre `security = True`
  
- TRANSPORT DATA GOUV : (facultatif)
  - Dans update_pt_datasets.py, changer `security = True` en `security = False`, puis exécuter UNE SEULE FOIS save_data_from_csv_to_db_mobpro.py (PREND UN PEU DE TEMPS)
  - Certains sets de données rencontreront un problème lors de l'enregistrement, ignorer

Les autres tables seront remplies lors de l'exécution du code Python, lors des calls aux API.

**6 - Utilisation**

- Dans votre environnement de développement Python, run main.py
- Démarrer React :
  - Ouvrir l'invite de commandes (cmd)
  - Se rendre dans le dossier de l'interface `cd votre_chemin/0.6Planet/interface/`
  - `npm start`
  - Une fenêtre s'ouvre dans votre navigateur : elle affiche les résultats produits une fois que l'éxecution du fichier main.py est terminée
- Pour faire des modifications de code, travaillez chacun.e sur une branche Git différente (ex : une branche hvds, une Champs Romain)


## Description

Cet outil établit un diagnostic des pratiques de mobilité sur un territoire donné. 

Il rassemble les lieux d'activité du territoire, crée une population synthétique puis associe des trajets à la population. Enfin, il attribue des lieux à chaque trajet.
On exploite alors ces trajets pour effectuer des mesures pertinentes : émissions de GES, coût, et autres indicateurs...

