## Description du fichier des déplacements

### Les variables

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

### Traitement des données

Chaque déplacement de la liste représente au global *w_trav* déplacements. 
Lors de l'analyse des déplacements, il convient donc de pondérer les attributs quantitatifs par *w_trav*.

Par exemple, pour calculer la distance totale d'un ensemble de déplacements, on multiplie pour chaque déplacement 
la distance du déplacement par le coefficient de pondération, puis on somme les distances ainsi pondérées. 
Le nombre total de déplacements correspond lui à la somme des coefficients de pondération.

Chaque individu *id_ind* correspond bien à un seul individu, on pourrait donc attribuer une colonne *w_ind* = 1.
Ainsi pour avoir la distance moyenne par personne, on calcule la distance totale parcourue puis on divise par le nombre 
d'individus uniques.


### Indications pour le lien avec l'EMP

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


### Exemple de résultats obtenus 

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

