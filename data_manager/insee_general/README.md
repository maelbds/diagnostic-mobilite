## INSEE

### Description

INSEE folder contains all files to get INSEE data thanks to their API, process it, and store it into the database.

### Structure

- _api_request.py_ : proper INSEE API request, cf documentation in :
  - _doc/service_web_DDL.pdf_
  - _doc/doc_RP.xlsx_

### Other

_doc/geo_codes.csv_ contains all geo_codes and associated names, postal_code and coordinates according to following header : 

Code_commune_INSEE;Nom_commune;Code_postal;Ligne_5;Libellé_d_acheminement;coordonnees_gps
